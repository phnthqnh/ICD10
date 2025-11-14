import { CollectionViewer, SelectionChange } from '@angular/cdk/collections';
import { FlatTreeControl } from '@angular/cdk/tree';
import { BehaviorSubject, merge, Observable } from 'rxjs';
import { Icd10Service } from './icd-10.service';
import { DynamicFlatNode } from './icd-10.types';

export class ICD10DataSource {
    dataChange = new BehaviorSubject<DynamicFlatNode[]>([]);

    get data(): DynamicFlatNode[] { return this.dataChange.value; }

    set data(value: DynamicFlatNode[]) {
        this.treeControl.dataNodes = value;
        this.dataChange.next(value);
    }

    constructor(
        private treeControl: FlatTreeControl<DynamicFlatNode>,
        private icdService: Icd10Service
    ) {}

    initialize() {
        this.icdService.getChapters().subscribe(chapters => {
            const treeNodes = chapters.map(c =>
                new DynamicFlatNode(c.id, c.chapter, c.code, c.title_vi, 0, true)
            );

            this.dataChange.next(treeNodes);
        });
    }

    connect(collectionViewer: CollectionViewer): Observable<DynamicFlatNode[]> {
        this.treeControl.expansionModel.changed.subscribe(change => {
            if (change.added) {
                change.added.forEach(node => this.loadChildren(node));
            }
            if (change.removed) {
                change.removed.forEach(node => this.removeChildren(node));
            }
        });

        return this.dataChange;
    }

    disconnect() {}

    /** Khi expand node */
    loadChildren(node: DynamicFlatNode) {
        node.isLoading = true;

        let request: Observable<any[]>;

        if (node.level === 0)
            request = this.icdService.getBlocksByChapter(node.id);
        else if (node.level === 1)
            request = this.icdService.getDiseasesByBlock(node.id);
        else
            request = this.icdService.getDiseasesByDiseaseParent(node.id);

        request.subscribe(res => {
            const children = res.map(item =>
                new DynamicFlatNode(
                    item.id,
                    null,
                    item.code,
                    item.title_vi,
                    node.level + 1,
                    node.level < 2        // disease_child = level 3 => expandable = false
                )
            );

            const index = this.data.indexOf(node);
            this.data.splice(index + 1, 0, ...children);
            this.dataChange.next(this.data);

            node.isLoading = false;
        });
    }

    /** Khi collapse node */
    removeChildren(node: DynamicFlatNode) {
        const index = this.data.indexOf(node);
        let count = 0;

        for (let i = index + 1; i < this.data.length; i++) {
            if (this.data[i].level <= node.level) break;
            count++;
        }

        if (count > 0) {
            this.data.splice(index + 1, count);
            this.dataChange.next(this.data);
        }
    }
}
