import { Component, ViewEncapsulation, OnInit, ViewChild, inject, ElementRef } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';
import { UserService } from 'app/core/user/user.service';
import { animate, style, transition, trigger } from '@angular/animations';
import { TranslocoService, TranslocoModule } from '@ngneat/transloco';
import { AlertService } from 'app/core/alert/alert.service';

@Component({
    selector: 'app-user-info',
    standalone: true,
    imports: [CommonModule, FormsModule, TranslocoModule, MatTooltipModule, MatIconModule],
    templateUrl: './user-info.component.html',
    styleUrls: ['./user-info.component.scss'],
    encapsulation: ViewEncapsulation.None,
    animations: [
        trigger('fadeSlideIn', [
            transition(':enter', [
                style({ opacity: 0, transform: 'translateY(-10px)' }),
                animate(
                    '200ms ease-out',
                    style({ opacity: 1, transform: 'translateY(0)' })
                ),
            ]),
            transition(':leave', [
                animate(
                    '150ms ease-in',
                    style({ opacity: 0, transform: 'translateY(-10px)' })
                ),
            ]),
        ]),
    ],
})
export class UserInfoComponent implements OnInit {
    user: any;

    isLoading: boolean = false;
    isEditMode = false;
    isAvatarEditorVisible = false;
    avatarPreviewUrl = '';
    today: string = new Date().toISOString().split('T')[0];
    errorFields: { [key: string]: string } = {};
    globalErrorMessage: string = '';
    @ViewChild('inputAvatar') inputAvatar!: ElementRef<HTMLInputElement>;
    @ViewChild('inputFile') inputFile!: ElementRef<HTMLInputElement>;
    previewVerification: string | null = null;

    originalEmail: string = '';
    newEmail: string = '';

    verified_doctor: boolean = false;
    verifyPopup: boolean = false
    selectedFile: File | null = null;
    licenseNumber: string = '';
    hospitalName: string = '';
    role: number = 0;

    popupEmail: boolean = false;
    popupPreview: boolean = false;

    constructor(
        private _userService: UserService,
        private _translocoService: TranslocoService,
        private _alertService: AlertService,
    ) { }

    userInfoRows = [
        { key: 'username' },
        { key: 'first_name' },
        { key: 'last_name' },
        { key: 'email' },
        { key: 'is_verified_doctor' },
        { key: 'license_number' },
        { key: 'hospital' },
        { key: 'verification_file' },
    ];

    ngOnInit(): void {
        this.loadUserInfo();
    }

    loadUserInfo(): void {
        this._userService.role$.subscribe(role => {
            console.log("Role changed:", role);
            this.role = role;
        });
        this.isLoading = true;
        this._userService
            .get()
            // .pipe(switchMap(() => this._userService.itemUser$))
            .subscribe({
                next: (userData) => {
                    if (!userData) {
                        console.warn('No user data found.');
                        return;
                    }
                    this.user = userData;
                    console.log("USER DATA: ", this.user)
                    this.originalEmail = this.user.email;
                    if (this.user.license_number && this.user.hospital && this.user.verification_file) {
                        this.verified_doctor = true;
                    } else {
                        this.verified_doctor = false;
                    }
                    console.log('verified_doctor', this.verified_doctor);

                    this.isLoading = false;
                },
                error: () => {
                    console.error('User data load failed');
                    this.isLoading = false;
                },
            });
    }

    toggleEditMode(): void {
        this.isEditMode = !this.isEditMode;
        if (this.isEditMode) {
            if (this.user?.birthday) {
                const isoDate = new Date(this.user.birthday);
                const yyyy = isoDate.getFullYear();
                const mm = String(isoDate.getMonth() + 1).padStart(2, '0');
                const dd = String(isoDate.getDate()).padStart(2, '0');
                this.user.birthday = `${yyyy}-${mm}-${dd}`; // HTML input format
            }
        } else {
            this.errorFields = {};
            this.globalErrorMessage = '';
            this.avatarPreviewUrl = '';
            this.isAvatarEditorVisible = false;
            this.selectedFile = null;
            this.loadUserInfo();
        }
    }

    clearFieldError(field: string): void {
        if (this.errorFields[field]) {
            delete this.errorFields[field];
        }
    }
    // getStatus(statusId: number, key: string): string {
    //     const status = this._userService
    //         .getStatus()
    //         .find((s) => s.id === statusId);
    //     return status && key === 'name' ? status.name : status.class;
    // }

    cleanS3Url(url: string): string {
        return encodeURI(url);
    }

    isValidEmail(email: string): boolean {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    openPopUpEmail() {
        this.popupEmail = true
        this.newEmail = this.user.email
    }

    closePopUpEmail() {
        this.popupEmail = false;
        this.user.email = this.originalEmail
    }

    confirmEmail() {
        this.user.email = this.newEmail
        this.popupEmail = false
    }

    saveChanges(): void {
        if (!this.user) {
            console.warn('No user data to save.');
            return;
        }
        this.errorFields = {};

        // if (this.user.email !== this.originalEmail) {
        //     console.log("User changed email");

        //     // Validate format email
        //     if (!this.isValidEmail(this.user.email)) {
        //         this.errorFields['email'] = 'Email chưa đúng định dạng';
        //         return;
        //     }

        //     this.openPopUpEmail();
        // }
        if (!this.user.username) {
            this.errorFields['username'] = 'Vui lòng nhập tên đăng nhập';
            return;
        }

        if (this.user.username.length < 3 || this.user.username.length > 30) {
            this.errorFields['username'] = 'Tên đăng nhập phải từ 3 đến 30 ký tự';
            return;
        }

        if (this.user.username.includes(' ')) {
            this.errorFields['username'] = 'Tên đăng nhập không được chứa khoảng trắng';
            return;
        }

        // tên đăng nhập không được chứa ký tự đặc biệt
        const usernameRegex = /^[a-zA-Z0-9._-]+$/;
        if (!usernameRegex.test(this.user.username)) {
            this.errorFields['username'] = 'Tên đăng nhập không được chứa ký tự đặc biệt';
            return;
        }

        // tên đăng nhập không được là chỉ số
        const onlyNumbersRegex = /^[0-9]+$/;
        if (onlyNumbersRegex.test(this.user.username)) {
            this.errorFields['username'] = 'Tên đăng nhập không được là chỉ số';
            return;
        }

        const payload = {
            username: this.user?.username,
            first_name: this.user?.first_name,
            last_name: this.user?.last_name,
        };

        if (this.user?.verification_file) {
            this.user.verification_file = this.cleanS3Url(this.user.verification_file);
        }

        console.log("USER : ", payload);

        this._userService.update(payload).subscribe({
            next: () => {

                this.isEditMode = false;
                console.log("INFOR SAU KHI UPDATE: ", this.user);
                this.loadUserInfo();
                this._alertService.showAlert({
                    title: "Thành công",
                    message: "Cập nhật thành công!",
                    type: 'success',
                });
            },
            error: (err) => {
                console.error('Save user error:', err);

                if (
                    err?.error?.code === 'VALIDATION_ERROR' &&
                    Array.isArray(err.error.errors)
                ) {
                    err.error.errors.forEach((e: any) => {
                        const field = e.field;
                        const msg = e.message?.toLowerCase() || '';

                        if (field === 'username') {
                            if (msg.includes('đã tồn tại')) {
                                this.errorFields[field] = 'Tên đăng nhập đã tồn tại';
                            } else if (msg.includes('blank')) {
                                this.errorFields[field] = 'Vui lòng nhập tên đăng nhập';
                            }
                        }
                    });
                } else if (err?.error?.code === 'US_E_014') {
                    this.errorFields['email'] = 'Email đã tồn tại';
                } else {
                    this._alertService.showAlert({
                        title: "Thất bại",
                        message: "Cập nhật thất bại. Vui lòng thử lại.",
                        type: 'error',
                    });
                }
            },
        });
    }

    onFileSelected(event: Event): void {
        const input = event.target as HTMLInputElement;
        if (!input.files || input.files.length === 0) return;

        const file = input.files[0];

        // Validate size 5MB
        if (file.size > 5 * 1024 * 1024) {
            this.errorFields['avatar'] = 'Ảnh vượt quá dung lượng cho phép (tối đa 5MB).';
            return;
        }

        // Validate type
        if (!file.type.startsWith('image/')) {
            this.errorFields['avatar'] = 'Ảnh đại diện không hợp lệ. Chỉ hỗ trợ file .jpg, .png, .gif, .bmp, .tiff, .webp';
            return;
        }

        // Save old avatar to rollback if needed
        const oldAvatar = this.user.avatar;

        // Preview tạm thời
        const reader = new FileReader();
        reader.onload = () => {
            this.avatarPreviewUrl = reader.result as string;
        };
        reader.readAsDataURL(file);

        // Upload thật lên server
        const formData = new FormData();
        formData.append('file', file);

        this._userService.uploadAvatar(formData).subscribe({
            next: (res) => {
                if (res?.data?.avatar) {
                    this.user.avatar = res.data.avatar; // final URL from backend
                }

                this._alertService.showAlert({
                    title: "Thàng công",
                    message: "Thay đổi avatar thành công!",
                    type: 'success'
                })
            },
            error: (error) => {
                console.error('Upload avatar error:', error);

                // Rollback avatar cũ nếu upload fail
                this.user.avatar = oldAvatar;

                this._alertService.showAlert({
                    title: this._translocoService.translate('other.error_title'),
                    message: this._translocoService.translate('user_infor.error_avatar_upload'),
                    type: 'error',
                });
            },
        });
    }


    onVerificationFileSelected(event: Event): void {
        const input = event.target as HTMLInputElement;
        if (!input.files || input.files.length === 0) return;

        const file = input.files[0];

        // Validate size 5MB
        if (file.size > 5 * 1024 * 1024) {
            this.errorFields['file'] = 'Ảnh vượt quá dung lượng cho phép (tối đa 5MB).';
            return;
        }

        // Validate type
        if (!file.type.startsWith('image/')) {
            this.errorFields['file'] = 'File ảnh không hợp lệ. Chỉ hỗ trợ file .jpg, .png, .gif, .bmp, .tiff, .webp';
            return;
        }

        if (file) {
            this.selectedFile = file;
            const reader = new FileReader();
            reader.onload = (e: any) => this.previewVerification = e.target.result;
            reader.readAsDataURL(file);
        }
    }

    triggerAvatarEditor() {
        this.inputAvatar.nativeElement.click();
    }

    opendVerifyPopup() {
        this.verifyPopup = true
    }

    closeVerifyPopup() {
        this.verifyPopup = false
        this.licenseNumber = '';
        this.hospitalName = '';
        this.selectedFile = null;
    }

    triggerFileEditor() {
        this.inputFile.nativeElement.click();
    }

    haveVerified() : boolean {
        if (!this.user.verified_doctor && this.user.license_number && this.user.hospital && this.user.verification_file) {
            return true;
        } else {
            return false;
        }
    }

    verifyDoctor(event: Event): void {
        if (!this.selectedFile || !this.licenseNumber || !this.hospitalName) {
            this._alertService.showAlert({
                title: "Thiếu dữ liệu",
                message: "Vui lòng nhập đủ dữ liệu.",
                type: 'error'
            });
            return;
        }
        console.log('selectedFile', this.selectedFile);
        console.log('licenseNumber', this.licenseNumber);
        console.log('hospitalName', this.hospitalName);
        const formData = new FormData();
        formData.append("file", this.selectedFile);
        formData.append("license_number", this.licenseNumber);
        formData.append("hospital", this.hospitalName);

        console.log('formData', formData);
        this._userService.verifyDoctor(formData).subscribe({
            next: (res) => {

                this._alertService.showAlert({
                    title: "Thàng công",
                    message: "Gửi yêu cầu xác minh bác sĩ thành công!",
                    type: 'success'
                })
                this.user.license_number = this.licenseNumber;
                this.user.hospital = this.hospitalName;
                this.user.verification_file = this.selectedFile.name;
                console.log('user', this.user);
                this.verified_doctor = false;
                this.closeVerifyPopup();
            },
            error: (error) => {
                console.error('Upload avatar error:', error);

                this._alertService.showAlert({
                    title: "Thất bại",
                    message: "Gửi yêu cầu xác minh bác sĩ thất bại. Vui lòng thử lại.",
                    type: 'error',
                });
            },
        });
    }

    openImagePreview() {
        this.popupPreview = true;
    }

    closeImagePreview() {
        this.popupPreview = false;
    }
}
