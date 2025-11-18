import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { AlertService } from 'app/core/alert/alert.service';
import { FuseAlertComponent } from '../../../../@fuse/components/alert/alert.component';
import { fuseAnimations } from '@fuse/animations';

@Component({
    selector: 'app-global-alert',
    standalone: true,
    imports: [CommonModule, FuseAlertComponent],
    animations: fuseAnimations,

    template: `
        <fuse-alert
            *ngIf="_alertService.alert$ | async as alert"
            [appearance]="'soft'"
            [dismissible]="true"
            [dismissed]="false"
            [type]="alert.type"
            (dismissedChange)="alertService.hideAlert()"
            @slideOutRight
        >
            <span fuseAlertTitle>{{ alert.title }}</span>
            {{ alert.message }}
        </fuse-alert>
    `,
})
export class GlobalAlertComponent {
    constructor(public _alertService: AlertService) {}
}
