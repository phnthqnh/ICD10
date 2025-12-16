import { Overlay, OverlayRef } from '@angular/cdk/overlay';
import { TemplatePortal } from '@angular/cdk/portal';
import { DatePipe, NgClass, NgFor, NgIf, NgTemplateOutlet } from '@angular/common';
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

@Component({
    selector       : 'notifications',
    templateUrl    : './notifications.component.html',
    encapsulation  : ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.OnPush,
    exportAs       : 'notifications',
    standalone     : true,
    imports        : [MatButtonModule, NgIf, MatIconModule, MatTooltipModule, NgFor, NgClass, NgTemplateOutlet, RouterLink, DatePipe],
})
export class NotificationsComponent implements OnInit, OnDestroy
{
    @ViewChild('notificationsOrigin') private _notificationsOrigin: MatButton;
    @ViewChild('notificationsPanel') private _notificationsPanel: TemplateRef<any>;

    notifications: Notification[];
    unreadCount: number = 0;
    isLoggedIn: boolean = false;
    private _overlayRef: OverlayRef;
    private _unsubscribeAll: Subject<any> = new Subject<any>();

    /**
     * Constructor
     */
    constructor(
        private _changeDetectorRef: ChangeDetectorRef,
        private _notificationsService: NotificationsService,
        private _overlay: Overlay,
        private _viewContainerRef: ViewContainerRef,
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

        // ✅ Initialize WebSocket nếu đã đăng nhập
        if (this.isLoggedIn) {
            this._notificationsService.initializeWebSocket();
        }

        // this._notificationsService.getAll().subscribe((res) => {
        //     this.notifications = res?.data?.notifications;
        //     this.unreadCount = res?.data?.unread_count;
        //     console.log('fetch', this.notifications, this.unreadCount);
        //     this._changeDetectorRef.markForCheck();
        // })
        
        // ✅ Subscribe to notifications changes từ WebSocket
        this._notificationsService.notifications$
            .pipe(takeUntil(this._unsubscribeAll))
            .subscribe((notifications: Notification[]) => {
                this.notifications = notifications;
                console.log('🔄 Notifications updated from WebSocket:', notifications.length);
                this._changeDetectorRef.markForCheck();
            });

        // ✅ Subscribe to unread count changes
        this._notificationsService.unreadCount$
            .pipe(takeUntil(this._unsubscribeAll))
            .subscribe((count: number) => {
                const previousCount = this.unreadCount;
                this.unreadCount = count;
                
                if (count > previousCount && previousCount !== 0) {
                    console.log('📊 Unread count increased:', previousCount, '->', count);
                }
                
                this._changeDetectorRef.markForCheck();
            });

    }

    /**
     * On destroy
     */
    ngOnDestroy(): void
    {
        // Unsubscribe from all subscriptions
        this._unsubscribeAll.next(null);
        this._unsubscribeAll.complete();

         // ✅ Close WebSocket khi component destroy
        this._notificationsService.closeWebSocket();

        // Dispose the overlay
        if ( this._overlayRef )
        {
            this._overlayRef.dispose();
        }
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Open the notifications panel
     */
    openPanel(): void
    {
        // Return if the notifications panel or its origin is not defined
        if ( !this._notificationsPanel || !this._notificationsOrigin )
        {
            return;
        }

        // Create the overlay if it doesn't exist
        if ( !this._overlayRef )
        {
            this._createOverlay();
        }

        // Attach the portal to the overlay
        this._overlayRef.attach(new TemplatePortal(this._notificationsPanel, this._viewContainerRef));
    }

    /**
     * Sign in
     * 
     */
    signIn(): void
    {
        this._router.navigate(['/sign-in']);
    }

    /**
     * Close the notifications panel
     */
    closePanel(): void
    {
        this._overlayRef.detach();
    }

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
            next: () => { /* server đã ok; service nên đã emit cập nhật */ },
            error: () => {
                notification.is_read = prev; // rollback
                this._changeDetectorRef.markForCheck();
            }
        });
    }

    /**
     * Delete the given notification
     */
    delete(notification: any): void
    {
        // Delete the notification
        // this._notificationsService.delete(notification.id).subscribe();
        // ✅ Lưu index để rollback nếu cần
        const notificationIndex = this.notifications.findIndex(n => n.id === notification.id);
        const deletedNotification = { ...notification };
        
        // ✅ Xóa khỏi UI ngay lập tức
        this.notifications = this.notifications.filter(n => n.id !== notification.id);
        
        // ✅ Cập nhật unread count nếu notification chưa đọc
        if (!deletedNotification.is_read) {
            this.unreadCount = Math.max(0, this.unreadCount - 1);
        }
        
        // ✅ Trigger change detection
        this._changeDetectorRef.markForCheck();

        // Gửi request lên server
        this._notificationsService.delete(notification.id).subscribe({
            error: (err) => {
                // ❌ Nếu lỗi, rollback lại
                this.notifications.splice(notificationIndex, 0, deletedNotification);
                if (!deletedNotification.is_read) {
                    this.unreadCount++;
                }
                this._changeDetectorRef.markForCheck();
                console.error('Error deleting notification:', err);
            }
        });
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

    // -----------------------------------------------------------------------------------------------------
    // @ Private methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Create the overlay
     */
    private _createOverlay(): void
    {
        // Create the overlay
        this._overlayRef = this._overlay.create({
            hasBackdrop     : true,
            backdropClass   : 'fuse-backdrop-on-mobile',
            scrollStrategy  : this._overlay.scrollStrategies.block(),
            positionStrategy: this._overlay.position()
                .flexibleConnectedTo(this._notificationsOrigin._elementRef.nativeElement)
                .withLockedPosition(true)
                .withPush(true)
                .withPositions([
                    {
                        originX : 'start',
                        originY : 'bottom',
                        overlayX: 'start',
                        overlayY: 'top',
                    },
                    {
                        originX : 'start',
                        originY : 'top',
                        overlayX: 'start',
                        overlayY: 'bottom',
                    },
                    {
                        originX : 'end',
                        originY : 'bottom',
                        overlayX: 'end',
                        overlayY: 'top',
                    },
                    {
                        originX : 'end',
                        originY : 'top',
                        overlayX: 'end',
                        overlayY: 'bottom',
                    },
                ]),
        });

        // Detach the overlay from the portal on backdrop click
        this._overlayRef.backdropClick().subscribe(() =>
        {
            this._overlayRef.detach();
        });
    }

    /**
     * Calculate the unread count
     *
     * @private
     */
    private _calculateUnreadCount(): void
    {
        let count = 0;

        if ( this.notifications && this.notifications.length )
        {
            count = this.notifications.filter(notification => !notification.read).length;
        }

        this.unreadCount = count;
    }
}
