import { ChangeDetectorRef, ChangeDetectionStrategy, Component, ViewEncapsulation, OnInit } from '@angular/core';
import { CommonModule, NgFor, NgIf } from '@angular/common';
import { MatTreeModule, MatTreeFlatDataSource, MatTreeFlattener } from '@angular/material/tree';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { Icd10Service } from 'app/core/icd-10/icd-10.service';
import { DynamicFlatNode } from 'app/core/icd-10/icd-10.types';
import { RouterModule } from '@angular/router';
import { FlatTreeControl } from '@angular/cdk/tree';
import { ICD10DataSource } from 'app/core/icd-10/icd10.datasource';
import { Observable, of, map } from 'rxjs';
import { MatInputModule } from '@angular/material/input';
import { FeedBack } from 'app/core/feedback/feedback.types';
import { FeedbackService } from 'app/core/feedback/feedback.service';
import { AlertService } from 'app/core/alert/alert.service';

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

    searchTerm: string = '';

    dataSource!: ICD10DataSource;
    selected: any = null;

    showFeedbackPopup: boolean = false;

    feedBack: Partial<FeedBack> = {
        disease: null,
        block: null,
        chapter: null,
        code: '',
        title_vi: '',
        reason: ''
    };

    constructor(
        private _icdService: Icd10Service, 
        private _feedbackService: FeedbackService,
        private _alertService: AlertService
    ) { }

    ngOnInit(): void {
        this.dataSource = new ICD10DataSource(this.treeControl, this._icdService);
        this.dataSource.initialize();
    }

    hasChild = (_: number, node: DynamicFlatNode) => node.expandable;

    showDetail(id: number, level: number) {
        console.log('id', id);
        console.log('level', level);

        if (level === 0) {
            this._icdService.getDataChapter(id).subscribe(res => {
                console.log('data', res);
                this.selected = res
            });
        }

        if (level === 1) {
            this._icdService.getDataBlock(id).subscribe(res => {
                console.log('data', res);
                this.selected = res
            });
        }

        if (level === 2) {
            this._icdService.getDataDisease(id).subscribe(res => {
                console.log('data', res);
                this.selected = res
            });
        }

        if (level === 3) {
            this._icdService.getDataDiseaseChild(id).subscribe(res => {
                console.log('data', res);
                this.selected = res
            });
        }
    }

    openFeedbackPopup(selected: any) {
        console.log('selected', selected);
        this.showFeedbackPopup = true;
        if (selected.chapter) {
            this.feedBack = {
                disease: null,
                block: null,
                chapter: selected.chapter.id,
                code: selected.chapter.code || '',
                title_vi: selected.chapter.title_vi || '',
                reason: ''
            };
        }
        else if (selected.block) {
            this.feedBack = {
                disease: null,
                block: selected.block.id,
                chapter: null,
                code: selected.block.code || '',
                title_vi: selected.block.title_vi || '',
                reason: ''
            };
        }
        else if (selected.disease) {
            this.feedBack = {
                disease: selected.disease.id,
                block: null,
                chapter: null,
                code: selected.disease.code || '',
                title_vi: selected.disease.title_vi || '',
                reason: ''
            };
        }
        else if (selected.disease_parent) {
            this.feedBack = {
                disease: selected.disease_parent.id,
                block: null,
                chapter: null,
                code: selected.disease_parent.code || '',
                title_vi: selected.disease_parent.title_vi || '',
                reason: ''
            };
        }
        console.log('feedback', this.feedBack);
    }

    closeFeedbackPopup() {
        this.showFeedbackPopup = false;
        this.feedBack = {
            disease: null,
            block: null,
            chapter: null,
            code: '',
            title_vi: '',
            status: 3,
            reason: ''
        };
    }

    submitFeedback() {
        console.log('feedback', this.feedBack);
        if (!this.feedBack.reason || this.feedBack.reason.trim() === '') {
            this._alertService.showAlert({
                    title: "Thất bại",
                    message: "Vui lòng nhập lý do góp ý.",
                    type: 'error'
                });
            return;
        }
        this._feedbackService.submitFeedback(this.feedBack).subscribe(
            (res) => {
            console.log('submit feedback response', res);
            this._alertService.showAlert({
                    title: "Thàng công",
                    message: "Gửi góp ý thành công!",
                    type: 'success'
                });
            this.closeFeedbackPopup();
        },
        (error) => {
            console.error('submit feedback error', error);
            this._alertService.showAlert({
                    title: "Thất bại",
                    message: "Gửi góp ý thất bại. Vui lòng thử lại.",
                    type: 'error'
                });
        });
    }
}