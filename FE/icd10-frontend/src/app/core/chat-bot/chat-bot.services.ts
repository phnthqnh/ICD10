import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { ChatMessage, ChatSession, ChatResponse, User } from './chat-bot.types';
import { BehaviorSubject, map, switchMap, Observable, ReplaySubject, tap, of, throwError } from 'rxjs';
import { uriConfig } from '../uri/config';
import { ChatBotWebSocket } from './chat-bot.websocket';

@Injectable({providedIn: 'root'})
export class ChatBotService
{
    private _chat: BehaviorSubject<ChatMessage[]> = new BehaviorSubject(null);
    private _chats: BehaviorSubject<ChatSession[]> = new BehaviorSubject(null);
    private _profile: BehaviorSubject<User> = new BehaviorSubject(null);
    
    /**
     * Constructor
     */
    constructor(
        private _httpClient: HttpClient,
        public ws: ChatBotWebSocket,
    ) {}

    /**
     * Getter for chat
     */
    get chat$(): Observable<ChatMessage[]>
    {
        return this._chat.asObservable();
    }
    
    /**
     * Getter for chats
     */
    get chats$(): Observable<ChatSession[]>
    {
        return this._chats.asObservable();
    }
    
    /**
     * Getter for profile
     */
    get profile$(): Observable<User>
    {
        console.log('this._profile', this._profile);
        return this._profile;
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Get user chat_session list
     *
     * 
     */
    // getUserChatSessionList(): Observable<ChatSession[]>
    // {
    //     return this._httpClient.get<any>(uriConfig.API_GET_CHAT_SESSION)
    //         .pipe(
    //             map(res => {
    //                 this._profile = res.data[0]?.user ?? {};
                    
    //                 return res.data ?? []
    //                 })
    //         )
    // }
    getUserChatSessionList(): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_CHAT_SESSION)
            .pipe(
                tap((res) => {
                    this._chats.next(res.data ?? []);
                })
            )
    }

    /**
     * Get user chat_session list
     *
     * @param id
     */
    getChatMessage(id: number): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_CHAT_MESSAGES(id)).pipe(
            tap((res) => {
                this._chat.next(res.data ?? []);
                this.connectStream(id);
            }),
            switchMap((chat) => {
                
                if ( !chat )
                {
                    return throwError('Could not found chat with id of ' + id + '!');
                }
                
                return of(chat);
            })
        );
    }

    /**
     * Chat with ai
     * 
     * 
     */
    chatWithAi(data: any): Observable<ChatResponse>
    {
        return this._httpClient.post<any>(uriConfig.API_CHAT_WITH_AI, data)
            .pipe(
                map((res) => res ?? [])
            )
    }

    /**
     * Reset the selected chat
     */
    resetChat(): void
    {
        this._chat.next(null);
    }

    connectStream(sessionId: number) {
        this.ws.connect(sessionId);
    }

    addChatSession(session: any): void
    {
        // Nếu chats$ là BehaviorSubject, lấy giá trị hiện tại
        const currentChats = this._chats.value;
        this._chats.next([session, ...currentChats]);
    }
}