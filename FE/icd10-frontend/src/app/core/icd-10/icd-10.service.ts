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
     * Get chapter
     * 
     */
    getChapter(): Observable<Chapter[]>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_CHAPTER)
            .pipe(
                map((res) => res.data?.chapters ?? [])
            )
    }

    /**
     * Get block
     * 
     */
    getBlock(): Observable<Block[]>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_BLOCK)
            .pipe(
                map((res) => {
                    return res.data?.blocks ?? []
                })
            )
    }

    /**
     * Get disease
     * 
     */
    getDisease(): Observable<Disease[]>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_DISEASE)
            .pipe(
                map((res) => res.data?.diseases ?? [])
            )
    }

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
    getDataChapter(chapter: string): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_DATA_CHAPTER(chapter))
            .pipe(
                map((res) => res?.data ?? [])
            )
    }

    /**
     * get data block
     *
     * 
     */
    getDataBlock(code: string): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_DATA_BLOCK(code))
            .pipe(
                map((res) => res?.data ?? [])
            )
    }

    /**
     * get data disease
     *
     * 
     */
    getDataDisease(code: string): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_DATA_DISEASE(code))
            .pipe(
                map((res) => res?.data ?? [])
            )
    }

    /**
     * get data disease child
     *
     * 
     */
    getDataDiseaseChild(code: string): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_GET_ICD10_DATA_DISEASE_CHILD(code))
            .pipe(
                map((res) => res?.data ?? [])
            )
    }

    /**
     * search ICD
     * 
     * 
     */

    searchICD(query: string): Observable<any>
    {
        return this._httpClient.get<any>(uriConfig.API_ICD10_SEARCH, {
            params: { q: query }
        }).pipe(
            map((res) => res ?? [])
        )
    }
}