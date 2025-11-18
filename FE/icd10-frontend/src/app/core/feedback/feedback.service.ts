import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { FeedBack, Status } from './feedback.types';
import { BehaviorSubject, map, switchMap, Observable, ReplaySubject, tap } from 'rxjs';
import { uriConfig } from '../uri/config';

@Injectable({providedIn: 'root'})
export class FeedbackService
{
    private _httpClient = inject(HttpClient);
    
    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------


    /**
     * Get user feedback list
     *
     * 
     */
    getUserFeedbackList(): Observable<FeedBack[]>
    {
        return this._httpClient.get<any>(uriConfig.API_FEEDBACK_ICD10_LIST)
            .pipe(
                map((res) => res.data ?? [])
            )
    }
    
    /**
     * Submit feedback icd10
     *
     * 
     */
    submitFeedback(payload: any): Observable<any>
    {
        return this._httpClient.post<any>(uriConfig.API_FEEDBACK_ICD10_SUBMIT, payload)
    }

    getStatus(): Status[] {
        return [
            {
                id: 1,
                name: 'accept',
                class: 'bg-emerald-100 text-emerald-700',
                is_list: true,
            },
            {
                id: 2,
                name: 'reject',
                class: 'bg-red-100 text-red-700',
                is_list: false,
            },
            {
                id: 3,
                name: 'pending',
                class: 'bg-amber-100 text-amber-700',
                is_list: false,
            },
        ];
    }
}