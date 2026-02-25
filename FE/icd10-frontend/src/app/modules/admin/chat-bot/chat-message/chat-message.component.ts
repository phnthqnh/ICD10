import { ChangeDetectionStrategy, ChangeDetectorRef, Component, NgZone, OnDestroy, OnInit, ViewChild, ElementRef, ViewEncapsulation, HostListener } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ChatMessage, ChatSession, User } from 'app/core/chat-bot/chat-bot.types';
import { ChatBotService } from 'app/core/chat-bot/chat-bot.services';
import { MatSidenavModule } from '@angular/material/sidenav';
import { CommonModule, NgFor, NgIf } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { marked } from 'marked';
import { RouterModule } from '@angular/router';
import { TextFieldModule } from '@angular/cdk/text-field';
import { AlertService } from 'app/core/alert/alert.service';
import { ActivatedRoute } from '@angular/router';
import { FeedBack } from 'app/core/feedback/feedback.types';
import { FeedbackService } from 'app/core/feedback/feedback.service';
import { set } from 'lodash';
import { fuseAnimations } from '@fuse/animations';

@Component({
    selector       : 'chat-message',
    templateUrl    : './chat-message.component.html',
    encapsulation  : ViewEncapsulation.None,
    animations   : fuseAnimations,
    changeDetection: ChangeDetectionStrategy.OnPush,
    standalone     : true,
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
        TextFieldModule,
        MatTooltipModule
    ],
    styleUrls: ['./chat-message.component.scss']
})
export class ChatMessageComponent implements OnInit
{
    @ViewChild('messageInput') messageInput: ElementRef;
    @ViewChild('messagesPanel') private _messagesPanel: ElementRef;
    chat: ChatMessage[] = [];
    private _unsubscribeAll: Subject<any> = new Subject<any>();
    selectedFile: File = null;
    selectedFileUrl: string | null = null;
    chatId: number | null = null;
    streamingBotMsg: string = "";

    feedbackPopUp: boolean = false;
    selectedMessage: any = null;
    feedbackRating: number = 0;
    hoverRating: number = 0;         // để hiển thị hover
    feedbackComment: string = "";    // comment của user

    isLoading: boolean = false;

    highlightMessageId: number | null = null;

    /**
     * Constructor
     */
    constructor(
        private _changeDetectorRef: ChangeDetectorRef,
        private _chatService: ChatBotService,
        private _ngZone: NgZone,
        private _alertService: AlertService,
        private _feedbackService: FeedbackService,
        private _route: ActivatedRoute
    )
    {
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Decorated methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Resize on 'input' and 'ngModelChange' events
     *
     * @private
     */
    @HostListener('input')
    @HostListener('ngModelChange')
    private _resizeMessageInput(): void
    {
        // This doesn't need to trigger Angular's change detection by itself
        this._ngZone.runOutsideAngular(() => {

            setTimeout(() => {

                // Set the height to 'auto' so we can correctly read the scrollHeight
                this.messageInput.nativeElement.style.height = 'auto';

                // Detect the changes so the height is applied
                this._changeDetectorRef.detectChanges();

                // Get the scrollHeight and subtract the vertical padding
                this.messageInput.nativeElement.style.height = `${this.messageInput.nativeElement.scrollHeight}px`;

                // Detect the changes one more time to apply the final height
                this._changeDetectorRef.detectChanges();
            });
        });
    }

    // -----------------------------------------------------------------------------------------------------
    // @ Lifecycle hooks
    // -----------------------------------------------------------------------------------------------------

    /**
     * On init
     */
    ngOnInit(): void
    {
        this._route.paramMap.subscribe(params => {
            this.chatId = Number(params.get('id'));
            // When route param changes (new chat opened), ensure we scroll to bottom
            setTimeout(() => this.scrollToBottom(), 50);
        });
        // Chat - reconcile streaming placeholder with server messages to avoid duplicates
        this._chatService.chat$
            .pipe(takeUntil(this._unsubscribeAll))
            .subscribe((serverChat: ChatMessage[]) => {
                try {
                    const localStreaming = this.chat && this.chat.length ? this.chat[this.chat.length - 1] : null;

                    if (localStreaming && localStreaming.isStreaming) {
                        // Try to detect if server has already produced the final bot message that corresponds
                        const resolved = serverChat.find(m => m.role === 'bot' && m.id && localStreaming.content && m.content && (
                            m.content.trim().startsWith(localStreaming.content.trim()) ||
                            localStreaming.content.trim().startsWith(m.content.trim()) ||
                            m.content.trim() === localStreaming.content.trim()
                        ));

                        if (resolved) {
                            // Server has the final message -> use serverChat (authoritative)
                            this.chat = serverChat;
                        } else {
                            // Server hasn't persisted final bot message yet.
                            // Merge serverChat (authoritative history) and keep local streaming placeholder at the end to avoid duplication.
                            const merged = serverChat ? serverChat.slice() : [];
                            // Only append local streaming if its content isn't already present in serverChat
                            const exists = merged.some(m => m.content && localStreaming.content && m.content.trim() === localStreaming.content.trim());
                            if (!exists) {
                                merged.push(localStreaming);
                            }
                            this.chat = merged;
                        }
                    } else {
                        // No local streaming placeholder -> replace with server data
                        this.chat = serverChat;
                    }
                } catch (e) {
                    // fallback to replace
                    this.chat = serverChat;
                }

                // Mark for check and scroll
                this._changeDetectorRef.markForCheck();
                setTimeout(() => this.scrollToBottom(), 50);
            });
        
        this._chatService.ws.botChunk$
            .pipe(takeUntil(this._unsubscribeAll))
            .subscribe(chunk => {
                this._ngZone.run(() => {
                    // Cộng dồn streaming text bot
                    this.streamingBotMsg += chunk;

                    // Cập nhật UI (hiện message bot đang gõ)
                    this.updateStreamingMessage();
                });
            });

        this._chatService.ws.botDone$
            .pipe(takeUntil(this._unsubscribeAll))
            .subscribe(() => {
                this._ngZone.run(() => {
                    // Khi done → thêm message bot vào chat list
                    this.pushBotFinalMessage();
                });
            });

        // Đọc hash từ URL khi component load
        this.checkUrlHash();

        // ✅ Lắng nghe thay đổi hash (cho nút back/forward của browser)
        window.addEventListener('hashchange', () => {
            this.checkUrlHash();
        });
    }

    private checkUrlHash(): void {
        // Lấy hash từ URL (ví dụ: #id)
        const hash = window.location.hash;
        console.log('chat', this.chat);
        console.log('hash', hash);
        if (hash && hash.startsWith('#/')) {
            const id = Number(hash.substring(2));
            console.log('id', id);
            setTimeout(() => this.scrollToMessages(id), 100);
        }
    }

    /**
     * Scroll messages container to the message by id.
     */
    scrollToMessages(id: number): void {
        try {
            if (id === null || id === undefined) return;
            // Prefer the messages panel as the search root so we only look inside the chat viewport
            const container: HTMLElement = this._messagesPanel?.nativeElement;
            const selector = `[data-message-id="${id}"]`;
            let target: HTMLElement | null = null;

            if (container) {
                target = container.querySelector(selector) as HTMLElement;
            }

            // fallback to global id (older browsers or if attribute not present)
            if (!target) {
                target = document.getElementById(`msg-${id}`);
            }

            if (!target) return;

            // If the messages container uses column-reverse, scrollIntoView still works
            // but we ensure smooth scrolling and center the element for better UX.
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });

            // Highlight
            this.highlightMessageId = id;
            this._changeDetectorRef.markForCheck();
            console.log('highlightMessageId', this.highlightMessageId);

            // Remove highlight after 1.5s
            setTimeout(() => {
                if (this.highlightMessageId === id) {
                    this.highlightMessageId = null;
                }
            }, 1500);
        } catch (e) {
            // ignore errors
        }
    }


    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------

    /**
     * Reset the chat
     */
    resetChat(): void
    {
        this._chatService.resetChat();

        // Mark for check
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

    getMessageHtml(chat: any) {
        const raw = chat;
        if (!raw) return '';
        return marked.parse(raw); // convert markdown → HTML
    }

    getImage(image: string) {
        if (!image) return '';
        const img = encodeURI(image);
        return img;
    }

    onImageChange(event: Event) {
        const file = (event.target as HTMLInputElement).files[0];
        if (!file) return;
        if (!file.type.startsWith('image/')) {
            this._alertService.showAlert({
                title: 'Thất bại',
                message: 'Vui lý chọn ảnh',
                type: 'error',
            });
            return;
        }
        this.selectedFile = file;
        this.selectedFileUrl = URL.createObjectURL(file);
    }

    removeImage() {
        this.selectedFile = null;
        this.selectedFileUrl = null;
    }

    updateStreamingMessage() {
        if (this.isLoading) {
            this.isLoading = false;
        }
        // Nếu chunk rỗng thì KHÔNG tạo message bot
        if (!this.streamingBotMsg.trim()) return;

        const last = this.chat[this.chat.length - 1];
        // Nếu message cuối cùng là streaming bot → update
        if (last && last.role === 'bot' && last.isStreaming) {
            last.content = this.streamingBotMsg;
        } else {
            // Nếu chưa có → tạo message bot đang stream
            const date = new Date();
            this.chat.push({
                id: null,
                role: 'bot',
                content: this.streamingBotMsg,
                isStreaming: true,
                created_at: this.formatDate(date)
            });
        }

        this._changeDetectorRef.markForCheck();
        // keep view scrolled during streaming
        setTimeout(() => this.scrollToBottom(), 30);
    }

    pushBotFinalMessage() {
        const last = this.chat[this.chat.length - 1];

        if (last && last.isStreaming) {
            delete last.isStreaming;
        }

        // Reset biến stream
        this.streamingBotMsg = "";

        this._changeDetectorRef.markForCheck();
        // final message added → ensure scroll
        setTimeout(() => this.scrollToBottom(), 50);
    }

    /**
     * Scroll messages container to the bottom.
     */
    scrollToBottom(): void {
        try {
            const el = this._messagesPanel?.nativeElement;
            if (!el) return;
            // If using flex-col-reverse, bottom is at scrollTop = 0; otherwise scroll to max
            // We'll try both: if already at top, set to 0; otherwise set to scrollHeight
            // A short timeout ensures DOM has been updated.
            if (el.style.flexDirection && el.style.flexDirection.includes('column-reverse')) {
                // column-reverse: new items appear at top, ensure scrollTop = 0
                el.scrollTop = 0;
            } else {
                el.scrollTop = el.scrollHeight;
            }
        } catch (e) {
            // ignore
        }
    }

    formatDate(date: Date) {
        return date.toISOString();
    }

    sendMessage(message: string) {
        if (!message.trim() && !this.selectedFile) return;

        const date = new Date();
        this.chat.push({
            role: 'user',
            content: message,
            image: this.selectedFile ? URL.createObjectURL(this.selectedFile) : null,
            created_at: this.formatDate(date)
        });
        this._changeDetectorRef.markForCheck();
        
        const formData = new FormData();
        formData.append("text", message);
        formData.append("session_id", this.chatId.toString());
        if (this.selectedFile) 
            formData.append("image", this.selectedFile);
        console.log('formData', formData);

        this.messageInput.nativeElement.value = '';
        this.removeImage();

        // bắt đầu loading
        this.isLoading = true;
        this._changeDetectorRef.markForCheck();

        this._chatService.chatWithAi(formData).subscribe({
            next: (res: any) => {
                this.isLoading = false;
                console.log('res', res);
                console.log('last', this.chat[this.chat.length - 1]);
                const last = this.chat[this.chat.length - 1];
                last.id = res.message_id;
                this._changeDetectorRef.markForCheck();
            },
            error: (err) => {
                console.error('Error creating chat:', err?.error?.error);
                this.isLoading = false;
                this.chat.pop();
                if (err?.status === 429) {
                    this._alertService.showAlert({
                        title: 'Thất bại',
                        message: err?.error?.error,
                        type: 'error',
                    })
                } else {
                    this._alertService.showAlert({
                        title: "Thất bại",
                        message: "Đã có lỗi xảy ra, vui lòng thử lại sau ít phút.",
                        type: 'error'
                    })   
                }
            }
        });
        this.messageInput.nativeElement.value = '';
    }

    canSend(message: string): boolean {
        const hasText = message.trim();
        return hasText && !this.isLoading;
    }

    openFeedback(message: any) {
        console.log('openFeedback', message);
        this.feedbackPopUp = true;
        this.selectedMessage = message;
    }

    closeFeedbackPopup() {
        this.feedbackPopUp = false;
        this.selectedMessage = null;
        this.feedbackRating = 0;
        this.feedbackComment = '';
        // Ensure OnPush components update immediately
        this._changeDetectorRef.markForCheck();
    }

    setRating(star: number) {
        this.feedbackRating = star;
    }

    submitFeedback() {
        if (!this.selectedMessage) return;
        if (!this.feedbackRating) {
            this._alertService.showAlert({
                title: "Thất bại",
                message: "Vui lòng chọn số sao đánh giá.",
                type: 'error'
            });
            return;
        };
        const payload = {
            chat_message: this.selectedMessage.id,
            rating: this.feedbackRating,
            comments: this.feedbackComment
        };
        console.log('payload', payload);
        this._feedbackService.submitFeedbackChatbot(payload).subscribe(
            (res) => {
                this.closeFeedbackPopup();
                this._alertService.showAlert({
                    title: "Thàng công",
                    message: "Gửi phản hồi thành công!",
                    type: 'success'
                });
            },
            (error) => {
                this._alertService.showAlert({
                    title: "Thất bại",
                    message: "Gửi phản hồi thất bại. Vui lòng thử lại.",
                    type: 'error'
                });
            });
    }
}
