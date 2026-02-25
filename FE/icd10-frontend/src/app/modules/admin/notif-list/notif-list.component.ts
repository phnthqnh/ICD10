import { Overlay, OverlayRef } from '@angular/cdk/overlay';
import { TemplatePortal } from '@angular/cdk/portal';
import { DatePipe, AsyncPipe, TitleCasePipe, NgClass, NgFor, NgIf, NgTemplateOutlet } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit, TemplateRef, ViewChild, ViewContainerRef, ViewEncapsulation } from '@angular/core';
import { MatButton, MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router, RouterLink } from '@angular/router';
import { NotificationsService } from 'app/layout/common/notifications/notifications.service';
import { Notification } from 'app/layout/common/notifications/notifications.types';
import { Subject, takeUntil } from 'rxjs';
import { AuthService } from 'app/core/auth/auth.service';
import { AlertService } from 'app/core/alert/alert.service';
import { DateTime } from 'luxon';

@Component({
    selector       : 'notif-list',
    templateUrl    : './notif-list.component.html',
    encapsulation  : ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.OnPush,
    standalone     : true,
    imports        : [
        MatButtonModule, 
        NgIf, 
        MatIconModule, 
        MatTooltipModule, 
        NgFor, 
        NgClass, 
        NgTemplateOutlet, 
        RouterLink, 
        AsyncPipe, 
        TitleCasePipe,
        DatePipe
    ],
})
export class NotifListComponent implements OnInit
{
    notifications: Notification[];
    unreadCount: number = 0;
    isLoggedIn: boolean = false;

    /**
     * Constructor
     */
    constructor(
        private _changeDetectorRef: ChangeDetectorRef,
        private _notificationsService: NotificationsService,
        private _authService: AuthService,
        private _router: Router,
        private _alertService: AlertService
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
        this.isLoggedIn = this._authService.isLoggedIn();

        // nếu chưa đăng nhập thì khóa cấu trúc
        if (!this.isLoggedIn) {
            return;
        }

        this._notificationsService.getAll().subscribe((res) => {
            this.notifications = res?.data?.notifications;
            this.unreadCount = res?.data?.unread_count;
            console.log('fetch', this.notifications, this.unreadCount);
            this._changeDetectorRef.markForCheck();
        })

    }

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------


    /**
     * Mark all notifications as read
     */
    markAllAsRead(): void
    {
        // Mark all as read
        this._notificationsService.markAllAsRead().subscribe();
    }

    /**
     * Toggle read status of the given notification
     */
    toggleRead(notification: any): void
    {
        // const previousState = notification.is_read;
        // const newState = !previousState;

        // notification.is_read = newState;

        // // Cập nhật số lượng unread
        // this.unreadCount += newState ? -1 : 1;
        // if (this.unreadCount < 0) this.unreadCount = 0;

        // this._changeDetectorRef.markForCheck();
        // this._notificationsService.markAsRead(notification.id, {is_read: newState}).subscribe({
        //     error: (err) => {
        //         // Nếu lỗi, rollback lại
        //         notification.is_read = previousState;
        //         this.unreadCount += previousState ? 1 : -1;
        //         if (this.unreadCount < 0) this.unreadCount = 0;

        //         this._changeDetectorRef.markForCheck();
        //         console.error('Error toggling read status:', err);
        //     }
        // });

        const prev = notification.is_read;
        const next = !prev;
        notification.is_read = next; // optimistic
        this._changeDetectorRef.markForCheck();

        this._notificationsService.markAsRead(notification.id, {is_read: next}).subscribe({
            next: () => { 
                this._alertService.showAlert({
                    title: 'Thành công',
                    message: 'Cập nhật trạng thái đã đọc thành công',
                    type: 'success'
                })
            },
            error: () => {
                notification.is_read = prev; // rollback
                this._changeDetectorRef.markForCheck();
            }
        });
    }

    /**
     * Returns whether the given dates are different days
     *
     * @param current
     * @param compare
     */
    isSameDay(current: string, compare: string): boolean
    {
        return DateTime.fromISO(current).hasSame(DateTime.fromISO(compare), 'day');
    }

    /**
     * Get the relative format of the given date
     *
     * @param date
     */
    getRelativeFormat(date: string): string
    {
        return DateTime.fromISO(date).setLocale('vi').toRelativeCalendar();
    }

    /**
     * Track by function for ngFor loops
     *
     * @param index
     * @param item
     */
    trackByFn(index: number, item: any): any
    {
        return item.id || index;
    }

    navigate(url: string): void {
        const parsed = new URL(url);

        if (parsed.pathname === '/icd-10') {
            // giữ nguyên format /icd-10#/0#1
            window.location.href = parsed.pathname + parsed.hash;
            return;
        }

        // feedback và các route khác dùng Angular Router
        const fragment = parsed.hash.replace(/^#\/?/, '');

        this._router.navigate(
            [parsed.pathname],
            { fragment }
        );
    }

}
