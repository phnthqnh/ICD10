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

@Component({
    selector: 'icd-10',
    templateUrl: './icd-10.component.html',
    encapsulation: ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.OnPush,
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

    constructor(private _icdService: Icd10Service) { }

    ngOnInit(): void {
        this.dataSource = new ICD10DataSource(this.treeControl, this._icdService);
        this.dataSource.initialize();
    }

    hasChild = (_: number, node: DynamicFlatNode) => node.expandable;

    showDetail(node: DynamicFlatNode) {
        console.log('node', node);

        if (node.level === 0) {
            this._icdService.getDataChapter(node.id).subscribe(res => {
                console.log('data', res.chapter.code);
                this.selected = res
            });
        }

        if (node.level === 1) {
            this._icdService.getDataBlock(node.id).subscribe(res => {
                console.log('data', res);
                this.selected = res
            });
        }

        if (node.level === 2) {
            this._icdService.getDataDisease(node.id).subscribe(res => {
                console.log('data', res);
                this.selected = res
            });
        }
    }
}