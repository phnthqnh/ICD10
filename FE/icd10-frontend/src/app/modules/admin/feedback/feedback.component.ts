import { ChangeDetectorRef, ChangeDetectionStrategy, Component, ViewEncapsulation, OnInit } from '@angular/core';
import { CommonModule, NgFor, NgIf } from '@angular/common';
import { MatTreeModule, MatTreeFlatDataSource, MatTreeFlattener } from '@angular/material/tree';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { RouterModule, Router } from '@angular/router';
import { MatInputModule } from '@angular/material/input';
import { FeedbackService } from 'app/core/feedback/feedback.service';
import { marked } from 'marked';

@Component({
    selector: 'feedback',
    templateUrl: './feedback.component.html',
    encapsulation: ViewEncapsulation.None,
    standalone: true,
    imports: [
        MatTreeModule,
        FormsModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        NgFor,
        NgIf,
        CommonModule,
        RouterModule,
        MatTabsModule,
    ],
})
export class FeedbackComponent implements OnInit{
    feedbackChapter: any[] = [];
    feedbackBlock: any[] = [];
    feedbackDisease: any[] = [];
    feedbackChatbot: any[] = [];

    // popup detail
    showDetailICDPopup: boolean = false;
    showDetailChatbotPopup: boolean = false;
    detailItem: any = null;
    detailType: 'chapter' | 'block' | 'disease' | 'chatbot' | null = null;
    detailLevel: number | null = null;

    // Track selected tab index
    selectedTabIndex: number = 0;

    constructor(
        private _feedbackService: FeedbackService,
        private _router: Router, // <-- added
    ) {}

    ngOnInit() {
        this._feedbackService.getUserFeedbackList().subscribe(res => {
            this.feedbackChapter = res.chapter_feedbacks;
            this.feedbackBlock = res.block_feedbacks;
            this.feedbackDisease = res.disease_feedbacks;

            // Parse hash after data is loaded
            this.parseHashAndNavigate();
        });
        this._feedbackService.getUserFeedbackChatbotList().subscribe(res => {
            console.log('res', res);
            this.feedbackChatbot = res;

            // Parse hash after data is loaded
            this.parseHashAndNavigate();
        })

        // Listen to hash changes
        window.addEventListener('hashchange', () => this.parseHashAndNavigate());
    }

    ngOnDestroy() {
        window.removeEventListener('hashchange', () => this.parseHashAndNavigate());
    }

    private parseHashAndNavigate(): void {
        const hash = window.location.hash;
        if (!hash || hash === '#') return;

        // Remove the leading '#' and split by '#'
        const parts = hash.substring(1).split('#');
        
        if (parts.length === 0) return;

        const tabIdentifier = parts[0];
        const itemId = parts.length > 1 ? parts[1] : null;

        // Map tab identifier to index
        let tabIndex = 0;
        let type: 'chapter' | 'block' | 'disease' | 'chatbot' | null = null;

        switch (tabIdentifier) {
            case '0':
                tabIndex = 0;
                type = 'chapter';
                break;
            case '1':
                tabIndex = 1;
                type = 'block';
                break;
            case '2':
                tabIndex = 2;
                type = 'disease';
                break;
            case 'c':
                tabIndex = 3;
                type = 'chatbot';
                break;
            default:
                return;
        }

        // Set the tab index
        this.selectedTabIndex = tabIndex;

        // If there's an item ID, open the detail popup
        if (itemId && type) {
            const item = this.findItemById(type, itemId);
            if (item) {
                if (type === 'chatbot') {
                    this.openDetailChatbot(item, false);
                } else {
                    this.openDetailICD(item, type, false);
                }
            }
        }
    }

    private findItemById(type: 'chapter' | 'block' | 'disease' | 'chatbot', id: string): any {
        const numId = parseInt(id, 10);
        
        switch (type) {
            case 'chapter':
                return this.feedbackChapter.find(item => item.id === numId);
            case 'block':
                return this.feedbackBlock.find(item => item.id === numId);
            case 'disease':
                return this.feedbackDisease.find(item => item.id === numId);
            case 'chatbot':
                return this.feedbackChatbot.find(item => item.id === numId);
            default:
                return null;
        }
    }

    onTabChange(index: number): void {
        // Update hash when tab changes
        // const tabMap = ['0', '1', '2', 'c'];
        // window.location.hash = `#${tabMap[index]}`;
        const tabMap = ['0', '1', '2', 'c'];
        const currentHash = window.location.hash;
        const parts = currentHash.substring(1).split('#');
        
        // If there's an item ID in current hash, preserve it
        if (parts.length > 1 && parts[1]) {
            window.location.hash = `#${tabMap[index]}#${parts[1]}`;
        } else {
            window.location.hash = `#${tabMap[index]}`;
        }
    }

    private _normalize(item: any, type: 'chapter'|'block'|'disease') {
        const out: any = {
            id: item.id ?? null,
            code: item.code ?? null,
            title_vi: item.title_vi ?? null,
            reason: item.reason ?? null,
            status: item.status ?? null,
            created_at: item.created_at ?? null,
            // canonical containers for relations
            chapter: null,
            block: null,
            disease: null
        };

        // If API already returns nested objects use them; if only id present wrap it
        const asObj = (val: any) => {
            if (val === null || val === undefined) return null;
            if (typeof val === 'object') return val;
            // numeric or string id -> return object with id (template can still use code/title from top-level)
            return { id: val };
        };

        // handle possible shapes
        if ('chapter' in item) out.chapter = asObj(item.chapter);
        if ('block' in item) out.block = asObj(item.block);
        if ('disease' in item) out.disease = asObj(item.disease);

        // some APIs embed the actual entity under different keys (e.g. block.block) - try to detect
        if (out.block && typeof out.block === 'object' && 'block' in out.block && (out.block as any).block) {
            out.block = asObj((out.block as any).block);
        }

        // Ensure type-specific fallbacks: for chapter items the chapter id may be in item.chapter (id only)
        if (type === 'chapter') {
            // prefer top-level code/title for display; chapter object mainly to show related chapter info if available
            if (!out.code && item.chapter && typeof item.chapter === 'object' && item.chapter.code) out.code = item.chapter.code;
            if (!out.title_vi && item.chapter && typeof item.chapter === 'object' && item.chapter.title_vi) out.title_vi = item.chapter.title_vi;
        }

        if (type === 'block') {
            // If block is an object with details, copy some fields for easy access
            if (out.block && typeof out.block === 'object') {
                out.block = {
                    id: out.block.id ?? out.block?.block ?? null,
                    code: out.block.code ?? out.block?.code ?? null,
                    title_vi: out.block.title_vi ?? out.block?.title_vi ?? null,
                    chapter: out.block.chapter ?? null
                };
            }
        }

        if (type === 'disease') {
            if (out.disease && typeof out.disease === 'object') {
                out.disease = {
                    id: out.disease.id ?? out.disease?.disease ?? null,
                    code: out.disease.code ?? out.code ?? null,
                    title_vi: out.disease.title_vi ?? out.title_vi ?? null,
                    block: out.disease.block ?? out.block ?? null,
                    disease_parent: out.disease.disease_parent ?? null
                };
            } else {
                // if only ids provided, keep them under numeric fields
                out.disease = out.disease; // may be {id: number} or null
            }
        }

        return out;
    }

    // trackBy for ngFor
    trackById(index: number, item: any) {
        return item?.id ?? index;
    }

    // helper to map status to label
    statusLabel(status: number | null | undefined): string {
        if (status === 1) return 'Đã duyệt';
        if (status === 2) return 'Đã từ chối';
        return 'Đang xử lý';
    }

    // helper to map status to tailwind/css classes
    statusClass(status: number | null | undefined): string {
        if (status === 1) return 'bg-green-100 text-green-700 border border-green-200';
        if (status === 2) return 'bg-red-100 text-red-700 border border-red-200';
        return 'bg-yellow-100 text-yellow-700 border border-yellow-200';
    }

    // open detail popup
    openDetailICD(item: any, type: 'chapter'|'block'|'disease', updateHash: boolean = true): void {
        this.detailItem = item;
        this.detailType = type;

        if (type === 'chapter') {
            this.detailLevel = 0;
        } else if (type === 'block') {
            this.detailLevel = 1;
        } else if (type === 'disease' && !item.disease_parent) {
            this.detailLevel = 2;
        } else {
            this.detailLevel = 3;
        }
        console.log('detailItem', this.detailItem);
        console.log('detailType', this.detailType);
        console.log('detailLevel', this.detailLevel);
        this.showDetailICDPopup = true;

        // Update hash with item ID
        if (updateHash) {
            const tabMap: {[key: string]: string} = {
                'chapter': '0',
                'block': '1',
                'disease': '2'
            };
            const currentHash = window.location.hash;
            const expectedHash = `#${tabMap[type]}#${item.id}`;
            
            // Only update if current hash is different
            if (currentHash !== expectedHash) {
                window.location.hash = expectedHash;
            }
        }
    }

    closeDetailPopup(): void {
        this.showDetailICDPopup = false;
        this.detailItem = null;
        this.detailType = null;

        // Remove item ID from hash, keep tab
        const hash = window.location.hash;
        if (hash && hash.includes('#')) {
            const tabIdentifier = hash.substring(1).split('#')[0];
            window.location.hash = `#${tabIdentifier}`;
        }
    }

    // optional: navigate to icd view (adjust route/query params as your app expects)
    viewInICD(): void {
        if (!this.detailItem || !this.detailType) return;
        const level = this.detailLevel;
        if (this.detailType === 'chapter') {
            var code = this.detailItem.chapter.chapter;
        } else var code = this.detailItem.code;
        // example: navigate to icd-10 and pass type/id as query params
        // this.closeDetailPopup();
        const url = `${window.location.origin}/icd-10#/${level}#${code}`;
        window.open(url, '_blank');
        // this._router.navigate(['/icd-10']).then(() => {
        //     window.location.hash = `#/${level}#${code}`;
        // });
    }

    // open detail popup
    openDetailChatbot(item: any, updateHash: boolean = true): void {
        this.detailItem = item;
        this.showDetailChatbotPopup = true;
        console.log('detailItem', this.detailItem);

        // Update hash with item ID
        if (updateHash) {
            const currentHash = window.location.hash;
            const expectedHash = `#c#${item.id}`;
            
            // Only update if current hash is different
            if (currentHash !== expectedHash) {
                window.location.hash = expectedHash;
            }
        }
    }

    closeDetailChatbot(): void {
        this.showDetailChatbotPopup = false;
        this.detailItem = null;

        // Remove item ID from hash, keep tab
        window.location.hash = `#c`;
    }

    getContentHtml(item: any, detail: boolean = false) {
        let raw = '';
        if (!detail) {
            if (item?.chat_message?.content.length > 50) {
                raw = item?.chat_message?.content.slice(0, 50) + '...';
            }
        } else {
            raw = item?.chat_message?.content;
        }
        if (!raw) return '';
        return marked.parse(raw); // convert markdown → HTML
    }

    viewChat(): void {
        if (!this.detailItem) return;
        const url = `${window.location.origin}/chat-bot/${this.detailItem?.session?.id}#/${this.detailItem?.chat_message?.id}`;
        window.open(url, '_blank');
    }

}