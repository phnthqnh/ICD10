import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'app/core/auth/auth.service';
import { AlertService } from 'app/core/alert/alert.service';

@Injectable({ providedIn: 'root' })
export class FeedbackGuard {
    constructor(
        private _authService: AuthService,
        private _router: Router,
        private _alertService: AlertService
    ) {}

    canActivate(): boolean {
        if (this._authService.isLoggedIn()) {
            return true;
        }
        
        // ✅ Show alert
        this._alertService.showAlert({
            title: "Thất bại",
            message: "Vui lòng đăng nhập để sử dụng tính năng này",
            type: 'error'
        });
        
        // Redirect to sign-in
        this._router.navigate(['/sign-in']);
        return false;
    }
}