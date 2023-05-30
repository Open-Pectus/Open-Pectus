/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';

import type { BatchJob } from '../models/BatchJob';

import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

@Injectable({
  providedIn: 'root',
})
export class BatchJobService {

    constructor(public readonly http: HttpClient) {}

    /**
     * Get Batch
     * @param id 
     * @returns BatchJob Successful Response
     * @throws ApiError
     */
    public getBatch(
id: number,
): Observable<BatchJob> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/batch_job/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Recent Batch Jobs
     * @returns BatchJob Successful Response
     * @throws ApiError
     */
    public getRecentBatchJobs(): Observable<Array<BatchJob>> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_batch_jobs',
        });
    }

}
