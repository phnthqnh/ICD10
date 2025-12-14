import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit, ViewEncapsulation } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ChatMessage, ChatSession, User } from 'app/core/chat-bot/chat-bot.types';
import { ChatBotService } from 'app/core/chat-bot/chat-bot.services';
import { MatSidenavModule } from '@angular/material/sidenav';
import { CommonModule, NgFor, NgIf } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { RouterModule, Router, ActivatedRoute  } from '@angular/router';

@Component({
    selector       : 'chat-session',
    templateUrl    : './chat-session.component.html',
    encapsulation  : ViewEncapsulation.None,
    standalone: true,
    imports        : [
        MatSidenavModule,
        CommonModule,
        MatIconModule,
        MatButtonModule,
        MatTabsModule,
        FormsModule,
        NgFor,
        NgIf,
        RouterModule,
        MatFormFieldModule,
        MatInputModule
    ],
})
export class ChatSessionComponent implements OnInit, OnDestroy
{
    chat_session: ChatSession[] = [];
    chat_messages: ChatMessage[] = [];
    drawerOpened: boolean = false;
    filteredChats: ChatSession[] = [];
    profile: User = null;
    selectedChat: ChatSession = null;
    private _unsubscribeAll: Subject<any> = new Subject<any>();

    /**
     * Constructor
     */
    constructor(
        private _chatbotService: ChatBotService,
        private _router: Router,
        private _activatedRoute: ActivatedRoute,
        private _changeDetectorRef: ChangeDetectorRef
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
        // Chatsession
        this._chatbotService.chats$
            .pipe(takeUntil(this._unsubscribeAll))
            .subscribe((chats: ChatSession[]) => {
                this.chat_session = this.filteredChats = chats;
                console.log('chats', chats);
                // Mark for check
                this._changeDetectorRef.markForCheck();
            });

        this.checkUrl();
        
    }

    private checkUrl(): void {
        const pathname = window.location.pathname;

        if (pathname && pathname !== '/chat-bot') {
            const url = pathname.substring(1); // Bỏ "#/" để lấy thông tin
            console.log('url', url);
            const id = url.split('/')[1];
            console.log('id', id);
            // đổi id sang kiểu number
            const idNumber = Number(id);
            this.selectedChat = this.chat_session.find(chat => chat.id === idNumber);
        } else {
            // Clear selection
            this.selectedChat = null;
        }
    }

    /**
     * On destroy
     */
    ngOnDestroy(): void
    {
        // Unsubscribe from all subscriptions
        // this._unsubscribeAll.next();
        this._unsubscribeAll.complete();
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Filter the chats
     *
     * @param query
     */
    filterChats(query: string): void
    {
        // Reset the filter
        if ( !query )
        {
            this.filteredChats = this.chat_session;
            return;
        }

        this.filteredChats = this.chat_session.filter(chat => chat.title.toLowerCase().includes(query.toLowerCase()));
    }

    /**
     * Open the new chat sidebar
     */
    openNewChat(): void
    {
        // ✅ Clear selectedChat để empty-message hiển thị
        this.selectedChat = null;
        // ✅ Navigate tới route '' (empty-message)
        this._router.navigate(['/chat-bot'], { relativeTo: null });
        this._changeDetectorRef.markForCheck();
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

    selectedChatSession(chat: ChatSession) {
        this.selectedChat = chat;
    }

}
