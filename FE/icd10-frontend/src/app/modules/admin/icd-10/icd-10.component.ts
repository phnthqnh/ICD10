import { ChangeDetectorRef, ChangeDetectionStrategy, Component, ViewEncapsulation, OnInit } from '@angular/core';
import { CommonModule, NgFor, NgIf } from '@angular/common';
import { MatTreeModule, MatTreeFlatDataSource, MatTreeFlattener } from '@angular/material/tree';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { Icd10Service } from 'app/core/icd-10/icd-10.service';
import { ICDNode, FlatNode } from 'app/core/icd-10/icd-10.types';
import { RouterModule } from '@angular/router';
import { FlatTreeControl } from '@angular/cdk/tree';
import { Observable, of, map } from 'rxjs';

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
    treeControl = new FlatTreeControl<FlatNode>(
        node => node.level,
        node => node.expandable
    );

    treeFlattener = new MatTreeFlattener(
        (node: ICDNode, level: number): FlatNode => ({
            // Xác định expandable dựa trên level thay vì children
            expandable: node.level !== 'disease_child', // Tất cả trừ disease_child đều expandable
            code: node.code,
            title_vi: node.title_vi,
            level,
            data: node
        }),
        node => node.level,
        node => node.expandable,
        node => node.children
    );

    selectedDisease: ICDNode | null = null;
    searchTerm: string = '';

    showDetail(node: ICDNode): void {
        this.selectedDisease = node;
        // Có thể gọi API chi tiết nếu muốn
        // this._icd10Service.getDiseaseDetail(node.id).subscribe(res => this.selectedDisease = res);
    }


    dataSource = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);

    constructor(
        private _icd10Service: Icd10Service,
        private _cdr: ChangeDetectorRef
    ) { }

    ngOnInit(): void {
        this._icd10Service.getChapters().subscribe((res) => {
            // --- ensure nodes typed as Icd10Node[] ---
            const nodes: ICDNode[] = res.map((c: any) => ({
                id: c.id,
                code: c.code,
                title_vi: c.title_vi,
                level: 'chapter'
            }));

            this.dataSource.data = nodes;
        });
    }

    hasChild = (_: number, node: FlatNode) => node.expandable;

    loadBlocks(chapter: ICDNode): Observable<ICDNode[]> {
        return this._icd10Service.getBlocksByChapter(chapter.id).pipe(
            map((res: any[]) => res.map(item => ({
            id: item.id,
            code: item.code,
            title_vi: item.title_vi,
            level: 'block' as const
            })))
        );
    }

    loadDiseases(block: ICDNode): Observable<ICDNode[]> {
        return this._icd10Service.getDiseasesByBlock(block.id).pipe(
            map((res: any[]) => res.map(item => ({
            id: item.id,
            code: item.code,
            title_vi: item.title_vi,
            level: 'disease' as const
            })))
        );
    }

    loadDiseaseChildren(disease: ICDNode): Observable<ICDNode[]> {
        return this._icd10Service.getDiseasesByDiseaseParent(disease.id).pipe(
            map((res: any[]) => res.map(item => ({
            id: item.id,
            code: item.code,
            title_vi: item.title_vi,
            level: 'disease_child' as const
            })))
        );
    }

    /** Bắt buộc gọi lại khi dữ liệu tree thay đổi */
    refreshTree() {
        this.dataSource.data = [...this.dataSource.data];
    }

    // khi click expand
    expandNode(node: FlatNode) {
        const data = node.data;
        // Nếu đang expanded thì collapse
        if (this.treeControl.isExpanded(node)) {
            this.treeControl.collapse(node);
            return;
        }

        // Nếu đã load children rồi thì chỉ expand
    if (data.children && data.children.length > 0) {
        this.treeControl.expand(node);
        return;
    }

        if (data.level === 'chapter') {
            this.loadBlocks(data).subscribe((children) => {
                data.children = children;
                this.refreshTree();
                this.treeControl.expand(node);
            });
        }
        else if (data.level === 'block') {
            this.loadDiseases(data).subscribe((children) => {
                data.children = children;
                this.refreshTree();
                this.treeControl.expand(node);
            });
        }
        else if (data.level === 'disease') {
            this.loadDiseaseChildren(data).subscribe((children) => {
                data.children = children;
                this.refreshTree();
                this.treeControl.expand(node);
            });
            console.log('node', node);
        }
    }
}