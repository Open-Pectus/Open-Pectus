/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';

import type { BatchJob } from '../models/BatchJob';
import type { Method } from '../models/Method';
import type { RunLog } from '../models/RunLog';

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
id: string,
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

    /**
     * Get Batch Job Method
     * @param id 
     * @returns Method Successful Response
     * @throws ApiError
     */
    public getBatchJobMethod(
id: string,
): Observable<Method> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/batch_job/{id}/method',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Batch Job Run Log
     * @param id 
     * @returns RunLog Successful Response
     * @throws ApiError
     */
    public getBatchJobRunLog(
id: string,
): Observable<RunLog> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/batch_job/{id}/run_log',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
