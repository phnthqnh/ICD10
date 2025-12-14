import { Injectable } from '@angular/core';
import { uriConfig } from '../uri/config';
import { AuthService } from 'app/core/auth/auth.service';
import { BehaviorSubject, map, switchMap, Observable, ReplaySubject, tap, of, throwError } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ChatBotWebSocket {

    private socket: WebSocket | null = null;
    private _botDone: BehaviorSubject<boolean> = new BehaviorSubject(false);
    private _botChunk: BehaviorSubject<string> = new BehaviorSubject('');

    constructor(private _authService: AuthService) {}

    get botDone$(): Observable<boolean> {
        return this._botDone.asObservable();
    }

    get botChunk$(): Observable<string> {
        return this._botChunk.asObservable();
    }

    connect(sessionId: number) {
        if (this.socket) {
            this.socket.close();
        }

        const token = this._authService.accessToken;
        if (!token) {
            console.warn('❌ No token available for WebSocket');
            return;
        }

        const wsUrl = uriConfig.WEBSOCKET_CHATBOTS + `?token=${token}&session_id=${sessionId}`;

        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
            console.log("WS connected:", wsUrl);
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("WS message:", data);
            this._handleWebSocketMessage(data);
        };

        this.socket.onerror = (err) => {
            console.error("WS error:", err);
        };

        this.socket.onclose = () => {
            console.log("WS closed");
        };
    }

    private _handleWebSocketMessage(data: any): void
    {
        console.log('📨 Received WebSocket message:', data);
        if (data.chunk !== undefined && !data.done) {
            this._botChunk.next(data.chunk);
        }

        // Hoàn tất message
        if (data.done) {
            this._botDone.next(data.done);
        }
    }

    close() {
        this.socket?.close();
        this.socket = null;
    }
}
