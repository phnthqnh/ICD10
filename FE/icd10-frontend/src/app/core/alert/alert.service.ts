// services/alert.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type AlertType = 'success' | 'error' | 'warning' | 'info';

export interface AlertData {
    title: string;
    message: string;
    type: AlertType;
    show: boolean;
}

@Injectable({
    providedIn: 'root'
})
export class AlertService {
    private alertSubject = new BehaviorSubject<AlertData | null>(null);
    alert$ = this.alertSubject.asObservable();

    showAlert(data: Omit<AlertData, 'show'>, timeout: number = 3000) {
        this.alertSubject.next({ ...data, show: true });

        setTimeout(() => {
            this.hideAlert();
        }, timeout);
    }

    hideAlert() {
        this.alertSubject.next(null);
    }
}
