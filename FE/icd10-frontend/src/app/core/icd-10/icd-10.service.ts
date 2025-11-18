import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Disease, Block, Chapter } from 'app/core/icd-10/icd-10.types';
import { BehaviorSubject, map, switchMap, Observable, ReplaySubject, tap } from 'rxjs';
import { uriConfig } from '../uri/config';

@Injectable({providedIn: 'root'})
export class Icd10Service
{
    private _httpClient = inject(HttpClient);
    private _disease = new BehaviorSubject<Disease[]>([]);
    diseases$ = this._disease.asObservable();
    private _block = new BehaviorSubject<Block[]>([]);
    blocks$ = this._block.asObservable();
    private _chapter = new BehaviorSubject<Chapter[]>([]);
    chapters$ = this._chapter.asObservable();
    
    // -----------------------------------------------------------------------------------------------------
    // @ Public methods
    // -----------------------------------------------------------------------------------------------------


    /**
     * Get all chapters
     *
     * 
     */
    getChapters(): Observable<Chapter[]>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_CHAPTERS)
            .pipe(
                // switchMap((res) => {
                //     const chapters = res.data?.chapters ?? [];
                //     this._chapter.next(chapters);
                //     return this._chapter.asObservable();
                // })
                map((res) => res.data?.chapters ?? [])
            )
    }

    /**
     * get all blocks by chapter
     *
     * 
     */
    getBlocksByChapter(id: number): Observable<Block[]>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_BLOCKS_BY_CHAPTER(id))
            .pipe(
                // switchMap((res) => {
                //     const blocks = res.data?.blocks ?? [];
                //     this._block.next(blocks);
                //     return this._block.asObservable();
                // })
                map((res) => res.data?.blocks ?? [])
            )
    }

    /**
     * get all diseases by block
     *
     * 
     */
    getDiseasesByBlock(id: number): Observable<Disease[]>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_DISEASES_BY_BLOCK(id))
            .pipe(
                // switchMap((res) => {
                //     const diseases = res.data?.diseases ?? [];
                //     this._disease.next(diseases);
                //     return this._disease.asObservable();
                // })
                map((res) => res.data?.diseases ?? [])
            )
    }

    /**
     * get all diseases by disease parent
     *
     * 
     */
    getDiseasesByDiseaseParent(id: number): Observable<Disease[]>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_DISEASES_CHILDREN(id))
            .pipe(
                // switchMap((res) => {
                //     const diseases = res.data?.diseases ?? [];
                //     this._disease.next(diseases);
                //     return this._disease.asObservable();
                // })
                map((res) => res.data?.diseases ?? [])
            )
    }

    /**
     * get data chapter
     *
     * 
     */
    getDataChapter(id: number): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_DATA_CHAPTER(id))
            .pipe(
                map((res) => res?.data ?? [])
            )
    }

    /**
     * get data block
     *
     * 
     */
    getDataBlock(id: number): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_DATA_BLOCK(id))
            .pipe(
                map((res) => res?.data ?? [])
            )
    }

    /**
     * get data disease
     *
     * 
     */
    getDataDisease(id: number): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_DATA_DISEASE(id))
            .pipe(
                map((res) => res?.data ?? [])
            )
    }

    /**
     * get data disease child
     *
     * 
     */
    getDataDiseaseChild(id: number): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_DATA_DISEASE_CHILD(id))
            .pipe(
                map((res) => res?.data ?? [])
            )
    }
}