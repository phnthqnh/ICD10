import { NgIf, NgFor } from '@angular/common';
import { Component, OnInit, ViewChild, ViewEncapsulation } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormsModule, ReactiveFormsModule, NgForm, UntypedFormGroup } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RouterLink } from '@angular/router';
import { fuseAnimations } from '@fuse/animations';
import { FuseAlertComponent, FuseAlertType } from '@fuse/components/alert';
import { AuthService } from 'app/core/auth/auth.service';
import { finalize } from 'rxjs';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
    selector     : 'auth-confirm-password',
    templateUrl  : './confirm-password.component.html',
    encapsulation: ViewEncapsulation.None,
    animations   : fuseAnimations,
    standalone   : true,
    imports      : [NgIf, NgFor, FuseAlertComponent, FormsModule, ReactiveFormsModule, MatFormFieldModule, MatIconModule, MatInputModule, MatButtonModule, MatProgressSpinnerModule, RouterLink],
})
export class AuthConfirmPasswordComponent implements OnInit
{

    confirmPasswordForm: UntypedFormGroup;
    otpArray = Array(6).fill(0);
    showAlert: boolean = false;
    alert: { type: FuseAlertType; message: string } = {
        type   : 'success',
        message: '',
    };
    constructor(
        private _formBuilder: FormBuilder,
        private _router: Router,
        private _route: ActivatedRoute,
        private _authService: AuthService
    ) { }

    // -----------------------------------------------------------------------------------------------------
    // @ Lifecycle hooks
    // -----------------------------------------------------------------------------------------------------

    /**
     * On init
     */
    ngOnInit(): void
    {
        // Create the form
        this.confirmPasswordForm = this._formBuilder.group({
            email: ['', [Validators.required, Validators.email]],
            newPassword: ['', Validators.required],
            otp0: ['', [Validators.required, Validators.pattern('[0-9]')]],
            otp1: ['', [Validators.required, Validators.pattern('[0-9]')]],
            otp2: ['', [Validators.required, Validators.pattern('[0-9]')]],
            otp3: ['', [Validators.required, Validators.pattern('[0-9]')]],
            otp4: ['', [Validators.required, Validators.pattern('[0-9]')]],
            otp5: ['', [Validators.required, Validators.pattern('[0-9]')]],
        });

        // If the user came from the forgot-password flow, prefill the email
        const emailFromQuery = this._route.snapshot.queryParamMap.get('email');
        if (emailFromQuery) {
            this.confirmPasswordForm.patchValue({ email: emailFromQuery });
        }
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Tự động di chuyển con trỏ sang ô kế tiếp / quay lại ô trước
     */
    moveFocus(event: KeyboardEvent, index: number): void {
        const input = event.target as HTMLInputElement;
        const value = input.value;

        // Nếu người dùng nhập số → chuyển sang ô tiếp theo
        if (value && index < 5) {
            const next = document.querySelectorAll('input[matInput]')[index + 1] as HTMLElement;
            next?.focus();
        }

        // Nếu người dùng nhấn Backspace khi ô trống → lùi lại
        if (!value && index > 0 && event.key === 'Backspace') {
            const prev = document.querySelectorAll('input[matInput]')[index - 1] as HTMLElement;
            prev?.focus();
        }
    }

    isOtpTouched(): boolean {
        for (let i = 0; i < 6; i++) {
            if (this.confirmPasswordForm.get('otp' + i)?.touched) {
                return true;
            }
        }
        return false;
    }

    isOtpEmpty(): boolean {
        if (!this.isOtpTouched()) return false;

        for (let i = 0; i < 6; i++) {
            if (!this.confirmPasswordForm.get('otp' + i)?.value) {
                return true;
            }
        }
        return false;
    }

    isOtpInvalidNumber(): boolean {
        if (!this.isOtpTouched()) return false;

        for (let i = 0; i < 6; i++) {
            const control = this.confirmPasswordForm.get('otp' + i);
            if (control?.hasError('pattern')) {
                return true;
            }
        }
        return false;
    }

    /**
     * Send the reset link
     */
    confirmReset(event: Event): void
    {
        event.preventDefault();
        event.stopPropagation();
        
        if (this.confirmPasswordForm.invalid) {
            this.alert = {
                type   : 'error',
                message: 'Vui lòng nhập đúng định dạng'
            }
            this.showAlert = true;
            return;
        }


        // Lấy giá trị từ form và tạo credentials object
        const formValue = this.confirmPasswordForm.value;

        // mật khẩu không được là chỉ số
        const onlyNumbersRegex = /^[0-9]+$/;
        if (onlyNumbersRegex.test(formValue.newPassword)) {
            this.showAlert = true;
            this.alert = {
                type   : 'error',
                message: 'Mật khẩu không được là chỉ số.',
            };
            return;
        }

        if (formValue.newPassword.length < 8) {
            // Show the alert
            this.showAlert = true;
            // Set the alert
            this.alert = {
                type   : 'error',
                message: 'Mật khẩu phải có ít nhất 8 ký tự.',
            };
            return;
        }

        // Gộp 6 ký tự OTP
        const otp = this.otpArray
            .map((_, i) => this.confirmPasswordForm.get('otp' + i)?.value)
            .join('');

        const payload = {
            email: formValue.email,
            new_password: formValue.newPassword,
            otp: otp
        };
        console.log(payload);
        // Disable the form
        this.confirmPasswordForm.disable();

        // Hide the alert
        this.showAlert = false;
        // Forgot password
        this._authService.confirmPassword(payload)
            .pipe(
                finalize(() => {
                    this.confirmPasswordForm.enable();
            }))    
            .subscribe({
                next: (res) => {
                    this._router.navigate(['/sign-in']);
                },
                error: (err) => {
                    console.error('❌ Lỗi xác nhận OTP:', err);

                    // Nếu backend trả về message → hiển thị
                    // if (err.error?.message) {
                    //     alert(err.error.message);
                    // }

                    // Xóa lỗi cũ (nếu có)

                    // Lấy thông tin lỗi từ backend
                    const code = err?.error?.code;
                    const message = err?.error?.errors[0]?.message;
                    console.log(code, message);
                    // ✅ Mapping lỗi theo mã code
                    switch (code) {
                        case 'OTP_EXPIRED': // OTP hết hạn
                            this.alert = { type: 'error', message: "Mã OTP đã hết hạn" }; // Hiển thị lỗi alert
                            this.showAlert = true;
                            break;

                        case 'OTP_INVALID': // OTP sai
                            this.alert = { type: 'error', message: message }; // Hiển thị lỗi alert
                            this.showAlert = true;
                            break;

                        default:
                            // Nếu lỗi khác (server, network, v.v.)
                            this.alert = { type: 'error', message: 'Đổi mật khâu thất bại, vui lòng thử lại!' }; // Hiển thị lỗi alert
                            this.showAlert = true;
                            break;
                    }
                }
            });
    }
}
