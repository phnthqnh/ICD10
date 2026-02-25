import { ChangeDetectionStrategy, ChangeDetectorRef, Component, NgZone, OnDestroy, OnInit, ViewChild, ElementRef, ViewEncapsulation } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ChatBotService } from 'app/core/chat-bot/chat-bot.services';
import { ChatMessage } from 'app/core/chat-bot/chat-bot.types';
import { AlertService } from 'app/core/alert/alert.service';
import { Router } from '@angular/router';
import { CommonModule, NgFor, NgIf } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { TextFieldModule } from '@angular/cdk/text-field';

@Component({
    selector: 'empty-message',
    templateUrl: './empty-message.component.html',
    encapsulation: ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.OnPush,
    standalone: true,
    imports: [
        CommonModule,
        MatIconModule,
        MatButtonModule,
        FormsModule,
        MatFormFieldModule,
        MatInputModule,
        TextFieldModule,
        NgFor,
        NgIf
    ]
})
export class EmptyMessageComponent implements OnInit, OnDestroy
{
    @ViewChild('messageInput') messageInput: ElementRef;
    
    private _unsubscribeAll: Subject<any> = new Subject<any>();
    selectedFile: File = null;
    selectedFileUrl: string | null = null;
    chat: ChatMessage[] = [];
    isLoading: boolean = false;

    constructor(
        private _changeDetectorRef: ChangeDetectorRef,
        private _chatService: ChatBotService,
        private _ngZone: NgZone,
        private _alertService: AlertService,
        private _router: Router
    ) {}

    ngOnInit(): void {}

    ngOnDestroy(): void {
        this._unsubscribeAll.next(null);
        this._unsubscribeAll.complete();
    }

    /**
     * Handle image change
     */
    onImageChange(event: Event): void {
        const file = (event.target as HTMLInputElement).files?.[0];
        if (!file) return;
        
        if (!file.type.startsWith('image/')) {
            this._alertService.showAlert({
                title: 'Thất bại',
                message: 'Vui lòng chọn ảnh',
                type: 'error',
            });
            return;
        }
        
        this.selectedFile = file;
        this.selectedFileUrl = URL.createObjectURL(file);
        this._changeDetectorRef.markForCheck();
    }

    /**
     * Remove selected image
     */
    removeImage(): void {
        this.selectedFile = null;
        this.selectedFileUrl = null;
        this._changeDetectorRef.markForCheck();
    }

    getImage(image: string) {
        if (!image) return '';
        const img = encodeURI(image);
        return img;
    }

    formatDate(date: Date) {
        return date.toISOString();
    }

    /**
     * Send new message and create chat session
     */
    sendMessage(message: string): void {
        if (!message.trim() && !this.selectedFile) return;

        const date = new Date();
        this.chat.push({
            id: null,
            role: 'user',
            content: message,
            image: this.selectedFile ? URL.createObjectURL(this.selectedFile) : null,
            created_at: this.formatDate(date)
        });
        this._changeDetectorRef.markForCheck();

        // ✅ B1: Tạo FormData để gửi API
        const formData = new FormData();
        formData.append("text", message);
        
        if (this.selectedFile) {
            formData.append("image", this.selectedFile);
        }

        this.isLoading = true;
        this._changeDetectorRef.markForCheck();

        this._chatService.chatWithAi(formData).subscribe({
            next: (res: any) => {
                console.log('New chat created:', res);

                // ✅ B3: Lấy session_id và tạo title từ 50 ký tự đầu
                const sessionId = res.session_id;
                console.log('sessionId', sessionId);
                const title = message.substring(0, 50);

                const newSession = {
                    id: sessionId,
                    title: title,
                    created_at: new Date().toISOString(),
                };

                // Thêm session vào chats list
                this._chatService.addChatSession(newSession);

                // Clear form
                // this.messageInput.nativeElement.value = '';
                // this.removeImage();

                this.isLoading = false;
                this._changeDetectorRef.markForCheck();

                this.chat.pop();

                // ✅ Navigate tới chat mới vừa tạo
                this._router.navigate(['/chat-bot', sessionId]);
            },
            error: (err) => {
                console.error('Error creating chat:', err);
                this.chat.pop();
                this.isLoading = false;
                this._changeDetectorRef.markForCheck();
                
                this._alertService.showAlert({
                    title: 'Thất bại',
                    message: 'Không thể tạo đoạn chat. Vui lòng thử lại sau ít phút.',
                    type: 'error'
                });
            }
        })
    }
    canSend(message: string): boolean {
        const hasText = message.trim();
        return hasText && !this.isLoading;
    }
}