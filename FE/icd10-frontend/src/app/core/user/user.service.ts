import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { User, Role } from 'app/core/user/user.types';
import { map, Observable, ReplaySubject, tap, catchError, of } from 'rxjs';
import { uriConfig } from '../uri/config';

@Injectable({providedIn: 'root'})
export class UserService
{
    private _httpClient = inject(HttpClient);
    private _user: ReplaySubject<User> = new ReplaySubject<User>(1);
    public itemUser$ = this._user.asObservable();

    // -----------------------------------------------------------------------------------------------------
    // @ Accessors
    // -----------------------------------------------------------------------------------------------------

    /**
     * Setter & getter for user
     *
     * @param value
     */
    set user(value: User)
    {
        // Store the value
        this._user.next(value);
    }

    get user$(): Observable<User>
    {
        return this._user.asObservable();
    }

    public role$ = this._user.pipe(
        map(user => user?.role ?? 0)
    );

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Get the current signed-in user data
     */
    get(): Observable<User>
    {
        return this._httpClient.get<User>(uriConfig.API_USER_INFOR).pipe(
            map((response: any) => {
                if (response?.data) {
                    const user = {
                        ...response.data,
                    };

                    this.user = user;

                    return user;
                }
                return null;
            }),
            catchError(() => of(null))
        );
    }

    /**
     * Update the user
     *
     * @param user
     */
    update(user: any): Observable<any> {
        return this._httpClient
            .put<User>(uriConfig.API_USER_INFOR_UPDATE, user)
            .pipe(
                map((response) => {
                    this._user.next(response);
                })
            );
    }

    /**
     * Upload avatar
     * 
     */
    uploadAvatar(payload: any): Observable<any> {
        return this._httpClient
            .put<any>(uriConfig.API_USER_INFOR_AVATAR, payload)
            .pipe(
                tap((response) => {
                    if (response?.data) {
                        this.user = response.data;
                    }
                }),
                catchError((error) => {
                    console.error('Error uploading avatar:', error);
                    return of(null);
                })
            );
    }

    /**
     * verify doctor
     * 
     */
    verifyDoctor(payload: any): Observable<any> {
        return this._httpClient
            .put<any>(uriConfig.API_VERIFY_DOCTOR, payload)
            .pipe(
                tap((response) => {
                    if (response?.data?.user) {
                        this.user = response.data.user;
                    }
                }),
                catchError((error) => {
                    console.error('Error verify doctor:', error);
                    return of(null);
                })
            );
    }

    /**
     * change password
     * 
     */
    changePassword(payload: any): Observable<any> {
        return this._httpClient
            .post<any>(uriConfig.API_CHANGE_PASSWORD, payload)
            .pipe(
                catchError((error) => {
                    console.error('Error change password:', error);
                    return of(null);
                })
            );
    }


}
