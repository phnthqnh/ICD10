import { NgIf } from '@angular/common';
import { Component, OnInit, ViewChild, ViewEncapsulation } from '@angular/core';
import { FormsModule, NgForm, ReactiveFormsModule, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router, RouterLink } from '@angular/router';
import { fuseAnimations } from '@fuse/animations';
import { FuseAlertComponent, FuseAlertType } from '@fuse/components/alert';
import { AuthService } from 'app/core/auth/auth.service';

@Component({
    selector     : 'auth-sign-up',
    templateUrl  : './sign-up.component.html',
    encapsulation: ViewEncapsulation.None,
    animations   : fuseAnimations,
    standalone   : true,
    imports      : [RouterLink, NgIf, FuseAlertComponent, FormsModule, ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatIconModule, MatCheckboxModule, MatProgressSpinnerModule],
})
export class AuthSignUpComponent implements OnInit
{
    @ViewChild('signUpNgForm') signUpNgForm: NgForm;

    alert: { type: FuseAlertType; message: string } = {
        type   : 'success',
        message: '',
    };
    signUpForm: UntypedFormGroup;
    showAlert: boolean = false;

    /**
     * Constructor
     */
    constructor(
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
        this.signUpForm = this._formBuilder.group({
                username      : ['', Validators.required],
                email     : ['', [Validators.required, Validators.email]],
                password  : ['', Validators.required],
            },
        );
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Sign up
     */
    signUp(): void
    {
        // Do nothing if the form is invalid
        if ( this.signUpForm.invalid )
        {
            return;
        }

        const onlyNumbersRegex = /^[0-9]+$/;
        if (onlyNumbersRegex.test(this.signUpForm.get('password').value)) {
            this.showAlert = true;
            this.alert = {
                type   : 'error',
                message: 'Mật khẩu không được chỉ chứa số.',
            }
            return;
        }

        // Disable the form
        this.signUpForm.disable();

        // Hide the alert
        this.showAlert = false;

        // Sign up
        this._authService.signUp(this.signUpForm.value).subscribe({
            next: () =>
                {
                    // Navigate to the confirmation required page
                    this._router.navigateByUrl('/verify-email');
                },
            error: (err) =>
                {
                    // Re-enable the form
                    this.signUpForm.enable();

                    // Reset the form
                    this.signUpNgForm.resetForm();

                    // xóa lỗi cũ
                    this.signUpForm.get('username').setErrors(null);
                    this.signUpForm.get('email').setErrors(null);
                    this.signUpForm.get('password').setErrors(null);

                    if (err?.error?.code === 'VALIDATION_ERROR') {
                        err?.error?.errors.forEach((e: any) => {
                            const field = e?.field;
                            if ( field === 'username' )
                            {
                                this.signUpForm.get('username').setErrors({serverError: "Tên đăng nhập đã tồn tại"});
                                this.signUpForm.get('username').markAsTouched();
                            }
                            else if ( field === 'email' )
                            {
                                this.signUpForm.get('email').setErrors({serverError: "Email đã tồn tại"});
                                this.signUpForm.get('email').markAsTouched();
                            }
                            else if ( field === 'password' )
                            {
                                this.signUpForm.get('password').setErrors({serverError: "Phải có ít nhất 8 ký tự"});
                                this.signUpForm.get('password').markAsTouched();
                            }
                        })
                    }

                    // Set the alert
                    this.alert = {
                        type   : 'error',
                        message: 'Vui lòng thử lại',
                    };

                    // Show the alert
                    this.showAlert = true;
                },
        });
    }
}
