import { ChangeDetectorRef, ChangeDetectionStrategy, Component, ViewEncapsulation, OnInit } from '@angular/core';
import { CommonModule, NgFor, Location, NgIf } from '@angular/common';
import { MatTreeModule, MatTreeFlatDataSource, MatTreeFlattener } from '@angular/material/tree';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { Icd10Service } from 'app/core/icd-10/icd-10.service';
import { DynamicFlatNode, Chapter, Block, Disease } from 'app/core/icd-10/icd-10.types';
import { RouterModule } from '@angular/router';
import { FlatTreeControl } from '@angular/cdk/tree';
import { ICD10DataSource } from 'app/core/icd-10/icd10.datasource';
import { Observable, of, map, forkJoin } from 'rxjs';
import { MatInputModule } from '@angular/material/input';
import { FeedBack } from 'app/core/feedback/feedback.types';
import { FeedbackService } from 'app/core/feedback/feedback.service';
import { AlertService } from 'app/core/alert/alert.service';
import { AuthService } from 'app/core/auth/auth.service';
import { UserService } from 'app/core/user/user.service';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
    selector: 'icd-10',
    templateUrl: './icd-10.component.html',
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
    ],
    styleUrls: ['./icd-10.component.scss']
})
export class Icd10Component implements OnInit {
    treeControl = new FlatTreeControl<DynamicFlatNode>(
        n => n.level,
        n => n.expandable
    );

    listChapter: Chapter[] = [];
    listBlock: Block[] = [];
    listDisease: Disease[] = [];
    newChapterSelection: any = {};
    dropdownOpenId: number | null = null;
    dropdownOpenDiseaseParentId: number | null = null;

    searchTerm: string = '';
    suggestions: any[] = [];
    typingTimer: any;

    dataSource!: ICD10DataSource;
    selected: any = null;

    // ✅ Thêm tracking cho selected node trong tree
    selectedNodeCode: string = '';
    selectedNodeLevel: number = -1;

    isExpandingTree: boolean = false; // ✅ Thêm biến này

    showFeedbackPopup: boolean = false;

    feedBack: Partial<FeedBack> = {
        disease: null,
        block: null,
        chapter: null,
        disease_parent: null,
        new_chapter: null,
        new_block: null,
        new_disease_parent: null,
        code: '',
        title_vi: '',
        reason: ''
    };

    isLoggedIn: boolean = false;
    role: number = 0;

    constructor(
        private _icdService: Icd10Service,
        private _feedbackService: FeedbackService,
        private _alertService: AlertService,
        private _authService: AuthService,
        private _userService: UserService,
        private _router: Router,
        private _route: ActivatedRoute,
        private _location: Location,
    ) { }

    ngOnInit(): void {
        this._userService.role$.subscribe(role => {
            console.log("Role changed:", role);
            this.role = role;
        });
        this.dataSource = new ICD10DataSource(this.treeControl, this._icdService);
        this.dataSource.initialize();
        this.isLoggedIn = this._authService.isLoggedIn();
        console.log('isLoggedIn', this.isLoggedIn, 'this.role', this.role);
        this.loadAllData();

        // Đọc hash từ URL khi component load
        this.checkUrlHash();

        // ✅ Lắng nghe thay đổi hash (cho nút back/forward của browser)
        window.addEventListener('hashchange', () => {
            this.checkUrlHash();
        });
    }

    loadAllData() {
        this._icdService.getChapter().subscribe(chapters => {
            this.listChapter = chapters;
        });

        this._icdService.getBlock().subscribe(blocks => {
            this.listBlock = blocks;
        });

        this._icdService.getDisease().subscribe(diseases => {
            this.listDisease = diseases;
        });
    }

    hasChild = (_: number, node: DynamicFlatNode) => node.expandable;

    /**
     * ✅ Kiểm tra xem node có đang được chọn không
     */
    isNodeSelected(node: DynamicFlatNode): boolean {
        if (node.level === 0) {
            return this.selectedNodeLevel === 0 && this.selectedNodeCode === node.chapter;
        }
        return this.selectedNodeLevel === node.level && this.selectedNodeCode === node.code;
    }

    /**
     * Kiểm tra và xử lý hash từ URL
     */
    private checkUrlHash(): void {
        // Lấy hash từ URL (ví dụ: #/A00)
        const hash = window.location.hash;

        if (hash && hash.startsWith('#/')) {
            const url = hash.substring(2); // Bỏ "#/" để lấy thông tin
            const level = url.split('#')[0];
            const code = url.split('#')[1];
            this.showDetail(code, parseInt(level));
        } else {
            // Clear selection
            this.selected = null;
            this.selectedNodeCode = '';
            this.selectedNodeLevel = -1;
        }
    }

    /**
     * ✅ Cập nhật URL hash
     */
    private updateUrlHash(code: string, level: number): void {
        this._location.replaceState(`/icd-10#/${level}#${code}`);
    }


    /**
     * ✅ Hiển thị chi tiết và cập nhật URL
     * @param updateUrl - Có cập nhật URL hay không (default: true)
     */
    showDetail(code: string, level: number, updateUrl: boolean = true) {

        // ✅ Cập nhật selected node ngay lập tức
        this.selectedNodeCode = code;
        this.selectedNodeLevel = level;

        if (level === 0) {
            this._icdService.getDataChapter(code).subscribe(res => {
                this.selected = res;
                if (updateUrl && res.chapter) {
                    this.updateUrlHash(res.chapter.chapter, 0);
                }
                // ✅ Expand và scroll đến node
                this.expandAndScrollToNode(res.chapter.chapter, 0);
            });
        }

        if (level === 1) {
            this._icdService.getDataBlock(code).subscribe(res => {
                this.selected = res;
                if (updateUrl && res.block) {
                    this.updateUrlHash(res.block.code, 1);
                }
                // ✅ Expand và scroll đến node
                this.expandAndScrollToNode(res.block.code, 1, res.block.chapter.chapter);
            });
        }

        if (level === 2) {
            this._icdService.getDataDisease(code).subscribe(res => {
                this.selected = res;
                if (updateUrl && res.disease) {
                    this.updateUrlHash(res.disease.code, 2);
                }
                console.log(res);
                // ✅ Expand và scroll đến node
                this.expandAndScrollToNode(res.disease.code, 2, res.disease.block.chapter.chapter);
            });
        }

        if (level === 3) {
            this._icdService.getDataDiseaseChild(code).subscribe(res => {
                this.selected = res;
                if (updateUrl && res.disease) {
                    this.updateUrlHash(res.disease.code, 3);
                }
                // ✅ Expand và scroll đến node
                this.expandAndScrollToNode(res.disease.code, 3, res.disease.block.chapter.chapter);
            });
        }
    }

    /**
 * ✅ Expand tree và scroll đến node được chọn - FIXED for Lazy Loading
 */
    private expandAndScrollToNode(code: string, level: number, chapter?: string): void {
        if (level === 0) {
            // Chapter level - có sẵn trong dataSource
            setTimeout(() => {
                this.scrollToNode(code, level);
            }, 100);
            return;
        }
        if (level === 1) {
            // Block level - cần expand chapter trước
            this.expandParentsSequentially(code, level, chapter).then(() => {
                // Sau khi expand xong, scroll đến node
                setTimeout(() => {
                    this.scrollToNode(code, level);
                }, 300);
            }).catch(() => {
                // Ẩn loading
                this.isExpandingTree = false;
            });
            return;
        }
        // Hiển thị loading
        this.isExpandingTree = true;

        // Với level > 0, cần expand parent trước
        this.expandParentsSequentially(code, level, chapter).then(() => {
            // Ẩn loading
            this.isExpandingTree = false;
            // Sau khi expand xong, scroll đến node
            setTimeout(() => {
                this.scrollToNode(code, level);
            }, 300);
        }).catch(() => {
            // Ẩn loading
            this.isExpandingTree = false;
        });
    }

    /**
         * ✅ Lấy mã chapter từ code (ví dụ: A00 -> A)
         */
    private getChapterFromCode(code: string): string {
        // ICD-10 code thường bắt đầu bằng 1 chữ cái
        return code.charAt(0);
    }

    /**
     * ✅ Expand các parent nodes tuần tự và đợi children load
     */
    private async expandParentsSequentially(code: string, level: number, chapter?: string): Promise<void> {
        console.log('code', code, 'level', level, 'chapter', chapter);
        if (level === 1) {
            // Block level - cần expand chapter
            if (chapter) {
                await this.expandChapter(chapter);
            } else {
                const chapterCode = this.getChapterFromCode(code);
                await this.expandChapter(chapterCode);
            }
        }
        else if (level === 2) {
            // Disease level - cần expand chapter -> block
            if (chapter) {
                await this.expandChapter(chapter);
            } else {
                const chapterCode = this.getChapterFromCode(code);
                await this.expandChapter(chapterCode);
            }

            const blockCode = await this.findBlockCodeForDisease(code);
            if (blockCode) {
                await this.expandBlock(blockCode);
            }
        }
        else if (level === 3) {
            if (chapter) {
                await this.expandChapter(chapter);
            } else {
                const chapterCode = this.getChapterFromCode(code);
                await this.expandChapter(chapterCode);
            }

            const diseaseParentCode = this.selected?.disease_parent?.code;
            if (diseaseParentCode) {
                const blockCode = await this.findBlockCodeForDisease(diseaseParentCode);
                if (blockCode) {
                    await this.expandBlock(blockCode);
                    await this.expandDisease(diseaseParentCode);
                }
            }
        }
    }

    /**
     * ✅ Expand chapter và đợi children load
     */
    private expandChapter(chapterCode: string): Promise<void> {
        return new Promise((resolve) => {
            const chapterNode = this.dataSource.data.find(n =>
                n.level === 0 && n.chapter === chapterCode
            );

            if (!chapterNode) {
                console.log('Chapter node not found:', chapterCode);
                resolve();
                return;
            }

            if (this.treeControl.isExpanded(chapterNode)) {
                console.log('Chapter already expanded:', chapterCode);
                resolve();
                return;
            }
            console.log('Expanding chapter:', chapterCode, chapterNode);

            // Subscribe để biết khi nào children được load
            let hasResolved = false;

            // Subscribe để biết khi nào children được load
            const subscription = this.dataSource.dataChange.subscribe(() => {
                if (hasResolved) return;
                // Kiểm tra xem children đã được load chưa
                const index = this.dataSource.data.indexOf(chapterNode);
                if (index >= 0 && index + 1 < this.dataSource.data.length) {
                    const nextNode = this.dataSource.data[index + 1];
                    if (nextNode.level === 1 && nextNode.code.startsWith(chapterCode)) {
                        console.log('Chapter children loaded:', chapterCode);
                        hasResolved = true;
                        subscription.unsubscribe();
                        resolve();
                    }
                }
            });

            this.treeControl.expand(chapterNode);

            // Timeout để tránh treo
            setTimeout(() => {
                if (!hasResolved) {
                    console.log('Chapter expand timeout:', chapterCode);
                    hasResolved = true;
                    subscription.unsubscribe();
                    resolve();
                }
            }, 2000);
        });
    }

    /**
     * ✅ Expand block và đợi children load
     */
    private expandBlock(blockCode: string): Promise<void> {
        return new Promise((resolve) => {
            const blockNode = this.dataSource.data.find(n =>
                n.level === 1 && n.code === blockCode
            );

            if (!blockNode) {
                console.log('Block node not found:', blockCode);
                resolve();
                return;
            }

            if (this.treeControl.isExpanded(blockNode)) {
                console.log('Block already expanded:', blockCode);
                resolve();
                return;
            }
            console.log('Expanding block:', blockCode, blockNode);

            // Subscribe để biết khi nào children được load
            let hasResolved = false;

            const subscription = this.dataSource.dataChange.subscribe(() => {
                if (hasResolved) return;
                const index = this.dataSource.data.indexOf(blockNode);
                if (index >= 0 && index + 1 < this.dataSource.data.length) {
                    const nextNode = this.dataSource.data[index + 1];
                    if (nextNode.level === 2) {
                        console.log('Block children loaded:', blockCode);
                        hasResolved = true;
                        subscription.unsubscribe();
                        resolve();
                    }
                }
            });

            this.treeControl.expand(blockNode);

            setTimeout(() => {
                if (!hasResolved) {
                    console.log('Block expand timeout:', blockCode);
                    hasResolved = true;
                    subscription.unsubscribe();
                    resolve();
                }
            }, 2000);
        });
    }

    /**
     * ✅ Expand disease và đợi children load
     */
    private expandDisease(diseaseCode: string): Promise<void> {
        return new Promise((resolve) => {
            const diseaseNode = this.dataSource.data.find(n =>
                n.level === 2 && n.code === diseaseCode
            );

            if (!diseaseNode) {
                console.log('Disease node not found:', diseaseCode);
                resolve();
                return;
            }

            if (this.treeControl.isExpanded(diseaseNode)) {
                console.log('Disease already expanded:', diseaseCode);
                resolve();
                return;
            }

            console.log('Expanding disease:', diseaseCode, diseaseNode);

            let hasResolved = false;
            const subscription = this.dataSource.dataChange.subscribe(() => {
                if (hasResolved) return;
                const index = this.dataSource.data.indexOf(diseaseNode);
                if (index >= 0 && index + 1 < this.dataSource.data.length) {
                    const nextNode = this.dataSource.data[index + 1];
                    if (nextNode.level === 3) {
                        console.log('Disease children loaded:', diseaseCode);
                        hasResolved = true;
                        subscription.unsubscribe();
                        resolve();
                    }
                }
            });

            this.treeControl.expand(diseaseNode);

            setTimeout(() => {
                if (!hasResolved) {
                    console.log('Disease expand timeout:', diseaseCode);
                    hasResolved = true;
                    subscription.unsubscribe();
                    resolve();
                }
            }, 2000);
        });
    }


    /**
     * ✅ Tìm block code chứa disease code
     */
    private async findBlockCodeForDisease(diseaseCode: string): Promise<string | null> {
        // Nếu đã có trong selected
        if (this.selected?.disease?.block?.code) {
            return this.selected.disease.block.code;
        }
        if (this.selected?.disease_parent?.block?.code) {
            return this.selected.disease_parent.block.code;
        }

        // Tìm trong listBlock đã load
        const block = this.listBlock.find(b => {
            const [start, end] = b.code.split('-');
            return diseaseCode >= start && diseaseCode <= end;
        });

        return block?.code || null;
    }


    /**
     * ✅ Scroll đến node trong tree
     */
    private scrollToNode(code: string, level: number): void {
        // Tìm element trong DOM
        const selector = level === 0
            ? `.mat-tree-node[data-chapter="${code}"]`
            : `.mat-tree-node[data-code="${code}"][data-level="${level}"]`;

        const element = document.querySelector(selector);

        if (element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
    }

    highlightMatch(text: string): string {
        if (!this.searchTerm) return text;

        const term = this.searchTerm.trim().toLowerCase();
        const regex = new RegExp(`(${term})`, "gi");

        return text.replace(regex, `<span class="font-bold text-primary-700">$1</span>`);
    }

    generateSuggestions() {
        if (!this.searchTerm.trim()) {
            this.suggestions = [];
            return;
        }

        const term = this.searchTerm.toLowerCase();
        this._icdService.searchICD(term).subscribe({
            next: (res: any) => {
                this.suggestions = res?.suggestions ?? [];
            },
            error: (err) => {
                console.error('Error fetching suggestions:', err);
                this.suggestions = [];
            }
        });
    }

    selectSuggestion(item: any) {
        this.searchTerm = `${item.code} ${item.title_vi}`;
        this.suggestions = [];
        this.showDetail(item.code, item.level);
    }

    onSearchChange() {
        clearTimeout(this.typingTimer);

        // Đợi 1 giây kể từ khi người dùng dừng nhập
        this.typingTimer = setTimeout(() => {
            this.generateSuggestions();
        }, 1000);
    }

    openFeedbackPopup(selected: any) {
        this.showFeedbackPopup = true;
        if (!this.isLoggedIn) {
            return;  // Không set feedBack nếu chưa login
        }
        if (selected.chapter) {
            this.feedBack = {
                chapter: selected.chapter.id,
                code: selected.chapter.code || '',
                title_vi: selected.chapter.title_vi || '',
                reason: ''
            };
        }
        else if (selected.block) {
            this.feedBack = {
                block: selected.block.id,
                chapter: selected.block.chapter,
                new_chapter: null,
                code: selected.block.code || '',
                title_vi: selected.block.title_vi || '',
                reason: ''
            };
        }
        else if (selected.disease && !selected.disease_parent) {
            this.feedBack = {
                disease: selected.disease.id,
                block: selected.disease.block || '',
                code: selected.disease.code || '',
                title_vi: selected.disease.title_vi || '',
                reason: ''
            };
        }
        else if (selected.disease_parent) {
            this.feedBack = {
                disease: selected.disease.id,
                disease_parent: selected.disease_parent,
                block: selected.disease_parent.block || '',
                code: selected.disease.code || '',
                title_vi: selected.disease.title_vi || '',
                reason: ''
            };
        }

    }

    closeFeedbackPopup() {
        this.showFeedbackPopup = false;
        this.dropdownOpenId = null;
        this.dropdownOpenDiseaseParentId = null;
        this.feedBack = {
            disease: null,
            disease_parent: null,
            block: null,
            chapter: null,
            new_chapter: null,
            new_block: null,
            new_disease_parent: null,
            code: '',
            title_vi: '',
            status: 3,
            reason: ''
        };
    }

    /**
    * Sign in
     */
    signIn(): void {
        this._router.navigate(['/sign-in']);
    }

    toggleDropdown(id: number) {
        this.dropdownOpenId = this.dropdownOpenId === id ? null : id;
    }

    isDropdownOpen(id: number) {
        return this.dropdownOpenId === id;
    }

    toggleDropdownDiseaseParent(id: number) {
        this.dropdownOpenDiseaseParentId = this.dropdownOpenDiseaseParentId === id ? null : id;
    }

    isDropdownOpenDiseaseParent(id: number) {
        return this.dropdownOpenDiseaseParentId === id;
    }

    selectNewChapter(feedBack: any, chapter: any) {
        feedBack.new_chapter = chapter;

        // đóng dropdown
        this.dropdownOpenId = null;

    }

    selectNewBlock(feedBack: any, block: any) {
        feedBack.new_block = block;

        // đóng dropdown
        this.dropdownOpenId = null;

    }

    selectNewDiseaseParent(feedBack: any, disease: any) {
        feedBack.new_disease_parent = disease;

        // đóng dropdown
        this.dropdownOpenId = null;
        this.dropdownOpenDiseaseParentId = null;
    }

    submitFeedback() {
        if (!this.feedBack.reason || this.feedBack.reason.trim() === '') {
            this._alertService.showAlert({
                title: "Thất bại",
                message: "Vui lòng nhập lý do góp ý.",
                type: 'error'
            });
            return;
        }
        if (this.feedBack.chapter && !this.feedBack.block) {
            console.log('this.feedBack', this.feedBack);
            this._feedbackService.submitFeedbackChapter(this.feedBack).subscribe(
                (res) => {
                    this._alertService.showAlert({
                        title: "Thàng công",
                        message: "Gửi góp ý thành công!",
                        type: 'success'
                    });
                    this.closeFeedbackPopup();
                },
                (error) => {
                    this._alertService.showAlert({
                        title: "Thất bại",
                        message: "Gửi góp ý thất bại. Vui lòng thử lại.",
                        type: 'error'
                    });
                });
        } else if (this.feedBack.block && !this.feedBack.disease) {
            const payload = {
                block: this.feedBack.block,
                chapter: this.feedBack.new_chapter ? this.feedBack.new_chapter.id : this.feedBack.chapter.id,   // gửi chapter người dùng đề xuất
                code: this.feedBack.code,
                title_vi: this.feedBack.title_vi,
                reason: this.feedBack.reason,
            };
            console.log('payload', payload);
            this._feedbackService.submitFeedbackBlock(payload).subscribe(
                (res) => {
                    this._alertService.showAlert({
                        title: "Thàng công",
                        message: "Gửi góp ý thành công!",
                        type: 'success'
                    });
                    this.closeFeedbackPopup();
                },
                (error) => {
                    this._alertService.showAlert({
                        title: "Thất bại",
                        message: "Gửi góp ý thất bại. Vui lòng thử lại.",
                        type: 'error'
                    });
                });
        } else if (this.feedBack.disease) {
            let disease_parent = null;
            if (!this.feedBack.new_disease_parent) {
                if (this.feedBack.disease_parent) {
                    disease_parent = this.feedBack.disease_parent;
                }
            } else {
                disease_parent = this.feedBack.new_disease_parent;
            }
            const payload = {
                disease: this.feedBack.disease,
                disease_parent: disease_parent ? disease_parent.id : null,
                block: this.feedBack.block.id ?? null,
                code: this.feedBack.code,
                title_vi: this.feedBack.title_vi,
                reason: this.feedBack.reason,
            };
            console.log('payload', payload);
            this._feedbackService.submitFeedbackDisease(payload).subscribe(
                (res) => {
                    this._alertService.showAlert({
                        title: "Thàng công",
                        message: "Gửi góp ý thành công!",
                        type: 'success'
                    });
                    this.closeFeedbackPopup();
                },
                (error) => {
                    this._alertService.showAlert({
                        title: "Thất bại",
                        message: "Gửi góp ý thất bại. Vui lòng thử lại.",
                        type: 'error'
                    });
                });
        }
    }
}