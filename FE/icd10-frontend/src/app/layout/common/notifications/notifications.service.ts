import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Notification } from 'app/layout/common/notifications/notifications.types';
import { map, Observable, ReplaySubject, switchMap, take, tap, Subject, BehaviorSubject } from 'rxjs';
import { AuthService } from 'app/core/auth/auth.service';
import { uriConfig } from 'app/core/uri/config';
import { AlertService } from 'app/core/alert/alert.service';

@Injectable({providedIn: 'root'})
export class NotificationsService
{
    private _notifications: ReplaySubject<Notification[]> = new ReplaySubject<Notification[]>(1);
    private _unreadCount: BehaviorSubject<number> = new BehaviorSubject<number>(0);
    private _webSocket: WebSocket;
    private _reconnectAttempts = 0;
    private _maxReconnectAttempts = 5;
    private _reconnectDelay = 3000;

    /**
     * Constructor
     */
    constructor(
        private _httpClient: HttpClient,
        private _authService: AuthService,
        private _alertService: AlertService
    ) {}

    // -----------------------------------------------------------------------------------------------------
    // @ Accessors
    // -----------------------------------------------------------------------------------------------------

    /**
     * Getter for notifications
     */
    get notifications$(): Observable<Notification[]>
    {
        return this._notifications.asObservable();
    }

    /**
     * Setter for notifications
     * 
     */
    set notifications(value: Notification[])
    {
        this._notifications.next(value);
    }

    // ✅ Thêm getter cho unreadCount
    get unreadCount$(): Observable<number>
    {
        return this._unreadCount.asObservable();
    }

    /**
     * Initialize WebSocket connection với token
     */
    initializeWebSocket(): void
    {
        if (this._webSocket && this._webSocket.readyState === WebSocket.OPEN) {
            return;
        }

        const token = this._authService.accessToken;
        if (!token) {
            console.warn('❌ No token available for WebSocket');
            return;
        }

        // ✅ Pass token qua URL query params (giống admin)
        // const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // const wsUrl = `${protocol}//${window.location.host}/ws/notifications/?token=${token}`;

        try {
            this._webSocket = new WebSocket(uriConfig.WEBSOCKET_NOTIFICATIONS + `?token=${token}`);
            this._webSocket.onopen = () => {
                console.log('✅ WebSocket connected');
                this._reconnectAttempts = 0;
            };

            this._webSocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this._handleWebSocketMessage(data);
            };

            this._webSocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
            };

            this._webSocket.onclose = () => {
                console.warn('⚠️ WebSocket disconnected');
                this._attemptReconnect();
            };
        } catch (error) {
            console.error('❌ Failed to create WebSocket:', error);
            this._attemptReconnect();
        }
    }

    /**
     * Handle incoming WebSocket messages (giống admin)
     */
    private _handleWebSocketMessage(data: any): void
    {
        console.log('📨 Received WebSocket message:', data);

        if (data.type === 'notifications_data') {
            // ✅ Initial data khi kết nối
            const notifications = this._mapNotifications(data.notifications);
            this._notifications.next(notifications);
            this._unreadCount.next(data.unread_count || 0);
        } else if (data.type === 'new_notification') {
            // ✅ Thông báo mới đến
            const notifications = this._mapNotifications(data.notifications);
            this._notifications.next(notifications);
            this._unreadCount.next(data.unread_count || 0);
            this._alertService.showAlert(
                {
                    title: "Thong báo", 
                    message: data.message, 
                    type: 'info'
                }
            );
        }
    }

    changeDateFormat(date: string): string {
        // Convert the date string to a Date object dd/MM/yyyy HH:mm
        const dateObj = new Date(date);
        const hours = dateObj.getHours().toString().padStart(2, '0');
        const minutes = dateObj.getMinutes().toString().padStart(2, '0');
        const day = dateObj.getDate().toString().padStart(2, '0');
        const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
        const year = dateObj.getFullYear().toString();
        return `${day}/${month}/${year} ${hours}:${minutes}`;
    }

    /**
     * Map backend notifications to frontend format
     */
    private _mapNotifications(backendNotifications: any[]): Notification[]
    {
        console.log('Mapped notifications:', backendNotifications);
        return backendNotifications.map(notif => ({
            id: notif.id.toString(),
            title: notif.title,
            description: notif.message,
            time: notif.created_at,
            read: notif.is_read,
            icon: 'heroicons_outline:bell',
            link: undefined,
            useRouter: false,
            unread_count: notif.unread_count,
            is_read: notif.is_read,
            created_at: notif.created_at,
            message: notif.message
        }));
    }

    /**
     * Attempt to reconnect WebSocket
     */
    private _attemptReconnect(): void
    {
        if (this._reconnectAttempts < this._maxReconnectAttempts) {
            this._reconnectAttempts++;
            console.log(`🔄 Reconnecting WebSocket... (Attempt ${this._reconnectAttempts}/${this._maxReconnectAttempts})`);
            setTimeout(() => {
                this.initializeWebSocket();
            }, this._reconnectDelay);
        } else {
            console.error('❌ Max WebSocket reconnection attempts reached');
        }
    }

    /**
     * Close WebSocket connection
     */
    closeWebSocket(): void
    {
        if (this._webSocket && this._webSocket.readyState === WebSocket.OPEN) {
            this._webSocket.close();
        }
    }

    /**
     * Get all notifications
     */
    getAll(): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_NOTIFICATIONS).pipe(
            // tap((notifications) =>
            // {
            //     const mapped = this._mapNotifications(notifications);
            //     this._notifications.next(mapped);
            // }),
            map((res) => {
                // console.log('Fetched notifications:', res);
                // const mapped = this._mapNotifications(res as any);
                // this._notifications.next(mapped);
                return res;
            })
        );
    }

    /**
     * Create a notification
     *
     * @param notification
     */
    create(notification: Notification): Observable<Notification>
    {
        return this.notifications$.pipe(
            take(1),
            switchMap(notifications => this._httpClient.post<Notification>('api/common/notifications', {notification}).pipe(
                map((newNotification) =>
                {
                    // Update the notifications with the new notification
                    this._notifications.next([...notifications, newNotification]);

                    // Return the new notification from observable
                    return newNotification;
                }),
            )),
        );
    }

    /**
     * Update the notification
     *
     */
    update(id: string, notification: Notification): Observable<Notification>
    {
        return this.notifications$.pipe(
            take(1),
            switchMap(notifications => this._httpClient.patch<any>(`api/notifications/${id}/`, {
                is_read: notification.read,
            }).pipe(
                map((updatedNotification: any) =>
                {
                    const index = notifications.findIndex(item => item.id === id);
                    if (index !== -1) {
                        notifications[index] = {
                            ...notifications[index],
                            read: updatedNotification.is_read
                        };
                        this._notifications.next(notifications);
                    }
                    return notification;
                }),
            )),
        );
    }

    /**
     * Delete the notification
     *
     * @param id
     */
    delete(id: string): Observable<boolean>
    {
        return this.notifications$.pipe(
            take(1),
            switchMap(notifications => this._httpClient.delete<boolean>('api/common/notifications', {params: {id}}).pipe(
                map((isDeleted: boolean) =>
                {
                    // Find the index of the deleted notification
                    const index = notifications.findIndex(item => item.id === id);

                    // Delete the notification
                    notifications.splice(index, 1);

                    // Update the notifications
                    this._notifications.next(notifications);

                    // Return the deleted status
                    return isDeleted;
                }),
            )),
        );
    }

    /**
     * Mark all notifications as read
     */
    // markAllAsRead(): Observable<boolean>
    // {
    //     return this.notifications$.pipe(
    //         take(1),
    //         switchMap(notifications => this._httpClient.get<boolean>('api/common/notifications/mark-all-as-read').pipe(
    //             map((isUpdated: boolean) =>
    //             {
    //                 // Go through all notifications and set them as read
    //                 notifications.forEach((notification, index) =>
    //                 {
    //                     notifications[index].read = true;
    //                 });

    //                 // Update the notifications
    //                 this._notifications.next(notifications);

    //                 // Return the updated status
    //                 return isUpdated;
    //             }),
    //         )),
    //     );
    // }

    markAsRead(id: number, body: any): Observable<boolean>
    {
        return this._httpClient.post<boolean>(uriConfig.API_MARK_NOTIFICATION_AS_READ(id), body);
    }

    markAllAsRead(): Observable<boolean>
    {
        return this._httpClient.post<boolean>(uriConfig.API_MARK_ALL_NOTIFICATIONS_AS_READ, {});
    }

    deleteNotification(id: number): Observable<boolean>
    {
        return this._httpClient.delete<boolean>(uriConfig.API_DELETE_NOTIFICATION(id));
    }
}
