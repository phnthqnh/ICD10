import { NgIf } from '@angular/common';
import { Component, OnInit, ViewChild, ViewEncapsulation } from '@angular/core';
import { FormsModule, NgForm, ReactiveFormsModule, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { fuseAnimations } from '@fuse/animations';
import { FuseAlertComponent, FuseAlertType } from '@fuse/components/alert';
import { AuthService } from 'app/core/auth/auth.service';

@Component({
    selector     : 'auth-sign-in',
    templateUrl  : './sign-in.component.html',
    encapsulation: ViewEncapsulation.None,
    animations   : fuseAnimations,
    standalone   : true,
    imports      : [RouterLink, FuseAlertComponent, NgIf, FormsModule, ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatIconModule, MatCheckboxModule, MatProgressSpinnerModule],
})
export class AuthSignInComponent implements OnInit
{
    @ViewChild('signInNgForm') signInNgForm: NgForm;

    alert: { type: FuseAlertType; message: string } = {
        type   : 'success',
        message: '',
    };
    signInForm: UntypedFormGroup;
    showAlert: boolean = false;

    /**
     * Constructor
     */
    constructor(
        private _activatedRoute: ActivatedRoute,
        private _authService: AuthService,
        private _formBuilder: UntypedFormBuilder,
        private _router: Router,
    )
    {
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Lifecycle hooks
    // -----------------------------------------------------------------------------------------------------

    /**
     * On init
     */
    ngOnInit(): void
    {
        // Create the form
        this.signInForm = this._formBuilder.group({
            email     : ['', [Validators.required, Validators.email]],
            password  : ['', Validators.required],
            rememberMe: [''],
        });
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Sign in
     */
    signIn(): void
    {
        // Return if the form is invalid
        if ( this.signInForm.invalid )
        {
            return;
        }

        // Disable the form
        this.signInForm.disable();

        // Hide the alert
        this.showAlert = false;

        // Lấy giá trị từ form và tạo credentials object
        const formValue = this.signInForm.value;
        const credentials = {
            email: formValue.email,
            password: formValue.password.trim(),
            rememberMe: formValue.rememberMe || false
        };

        // Sign in
        this._authService.signIn(credentials).subscribe({
            next: () => {
                const redirectURL =
                    this._activatedRoute.snapshot.queryParamMap.get('redirectURL') ||
                    '/signed-in-redirect';
                this._router.navigateByUrl(redirectURL);
            },
            error: (errorResponse) => {
                this.signInForm.enable();

                // Xóa lỗi cũ (nếu có)
                this.signInForm.get('email')?.setErrors(null);
                this.signInForm.get('password')?.setErrors(null);

                // Lấy thông tin lỗi từ backend
                const code = errorResponse?.error?.code;
                const message = errorResponse?.error?.message;
                const count_login = errorResponse?.error?.errors[0]?.message;
                const remaining_time = errorResponse?.error?.remaining_time;

                if (count_login) {
                    this.showAlert = true;
                    this.alert = {
                        type   : 'error',
                        message: `Số lần đăng nhập còn lại: ${count_login}`,
                    };
                }

                // ✅ Mapping lỗi theo mã code
                switch (code) {
                    case 'LOGIN_TOO_MANY_ATTEMPTS': // Too many attempts
                        this.showAlert = true;
                        this.alert = {
                            type   : 'error',
                            message: `Tài khoản tạm thời bị khóa do nhập quá nhiều thông tin sai. Vui lòng thử lại sau ${remaining_time} phút.`,
                        };
                        break;
                    case 'AU_E_005': // User not found
                        this.signInForm.get('email')?.setErrors({ serverError: message });
                        this.signInForm.get('email')?.markAsTouched();
                        break;

                    case 'AU_E_001': // Invalid username or password
                        this.signInForm.get('password')?.setErrors({ serverError: "Mật khẩu không đúng" });
                        this.signInForm.get('password')?.markAsTouched();
                        break;

                    default:
                        // Nếu lỗi khác (server, network, v.v.)
                        this.signInForm.setErrors({ serverError: 'Đăng nhập thất bại, vui lòng thử lại!' });
                        break;
                }
            },
        });
    }
}
