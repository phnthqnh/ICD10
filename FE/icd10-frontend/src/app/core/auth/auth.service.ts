import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { AuthUtils } from 'app/core/auth/auth.utils';
import { UserService } from 'app/core/user/user.service';
import { catchError, Observable, of, switchMap, throwError } from 'rxjs';
import { uriConfig } from '../uri/config';

@Injectable({providedIn: 'root'})
export class AuthService
{
    private _authenticated: boolean = false;
    private _httpClient = inject(HttpClient);
    private _userService = inject(UserService);
    private _remMe: boolean = false;

    // -----------------------------------------------------------------------------------------------------
    // @ Accessors
    // -----------------------------------------------------------------------------------------------------

    /**
     * Setter & getter for access token
     */
    set accessToken(token: string)
    {
        localStorage.setItem('accessToken', token);
    }

    get accessToken(): string
    {
        return localStorage.getItem('accessToken') ?? '';
    }

    /**
     * Setter & getter for refresh token
     */
    set refreshToken(token: string) {
        localStorage.setItem('refreshToken', token);
    }

    get refreshToken(): string {
        return localStorage.getItem('refreshToken') ?? '';
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Forgot password
     *
     * @param email
     */
    forgotPassword(payload: any): Observable<any>
    {
        return this._httpClient.post(uriConfig.API_FORGET_PASSWORD, payload);
    }

    /**
     * Confirm password
     *
     * 
     */
    confirmPassword(payload: any): Observable<any>
    {
        return this._httpClient.post(uriConfig.API_CONFIRM_PASSWORD, payload)
            .pipe(
            catchError((err: HttpErrorResponse) => {
                debugger // *
                // luôn trả về observable lỗi, không throw trực tiếp
                return throwError(() => err);
            })
        );
    }

    /**
     * Reset password
     *
     * @param password
     */
    resetPassword(password: string): Observable<any>
    {
        return this._httpClient.post('api/auth/reset-password', password);
    }

    /**
     * Sign in
     *
     * @param credentials
     */
    signIn(credentials: { email: string; password: string; rememberMe: boolean }): Observable<any>
    {
        // Throw error, if the user is already logged in
        if ( this._authenticated )
        {
            return throwError('User is already logged in.');
        }

        // không truyền rememberMe cho backend
        this._remMe = credentials.rememberMe;
        
        // Tạo object mới chỉ chứa email và password
        const loginCredentials = {
            email: credentials.email,
            password: credentials.password
        };

        return this._httpClient.post(uriConfig.API_USER_LOGIN, loginCredentials).pipe(
            switchMap((response: any) =>
            {
                // Store the access token in the local storage
                this.accessToken = response.data.token;

                if (this._remMe)
                    this.refreshToken = response.data.refresh_token;

                // Set the authenticated flag to true
                this._authenticated = true;

                // Store the user on the user service
                this._userService.user = response.data.user;

                // Return a new observable with the response
                console.log('response', response);
                return of(response);
            }),
        );
    }

    /**
     * Sign in using the access token
     */
    signInUsingToken(): Observable<boolean> {
        return this._httpClient.get(uriConfig.API_USER_INFOR).pipe(
            switchMap((response: any) => {
                this._authenticated = true;
                this._userService.user = response.data;
                return of(true);
            }),
            catchError(() => {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                this._authenticated = false;
                return of(false);
            })
        );
    }

    /**
     * Sign out
     */
    signOut(): Observable<any>
    {
        // Remove the access token from the local storage
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');

        // Set the authenticated flag to false
        this._authenticated = false;

        // Return the observable
        return of(true);
    }

    /**
     * Sign up
     *
     * @param user
     */
    signUp(user: { username: string; email: string; password: string;}): Observable<any>
    {
        return this._httpClient.post(uriConfig.API_USER_REGISTER, user);
    }

    /**
     * Unlock session
     *
     * @param credentials
     */
    unlockSession(credentials: { email: string; password: string }): Observable<any>
    {
        return this._httpClient.post('api/auth/unlock-session', credentials);
    }

    /**
     * Check the authentication status
     */
    check(): Observable<boolean>
    {
        // Check if the user is logged in
        if ( this._authenticated )
        {
            return of(true);
        }

        // Check the access token availability
        if ( !this.accessToken )
        {
            return of(false);
        }

        // Check the access token expire date
        if ( AuthUtils.isTokenExpired(this.accessToken) )
        {
            return of(false);
        }

        // If the access token exists, and it didn't expire, sign in using it
        return this.signInUsingToken();
    }

    /**
     * check logged in
     * 
     */
    isLoggedIn(): boolean {
        if (this._authenticated) {
            return true;
        }

        if (this.accessToken && !AuthUtils.isTokenExpired(this.accessToken)) {
            return true;
        }

        return false;
    }
}
