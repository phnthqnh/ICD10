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
    ],
})
export class FeedbackComponent implements OnInit{
    feedbackList: any[] = [];

    constructor(
        private _feedbackService: FeedbackService,
    ) {}

    ngOnInit() {
        this._feedbackService.getUserFeedbackList().subscribe(res => {
            this.feedbackList = res;
        });
    }

}