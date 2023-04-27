/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';

import type { BatchJob } from '../models/BatchJob';
import type { ProcessUnit } from '../models/ProcessUnit';
import type { ProcessValue } from '../models/ProcessValue';
import type { ProcessValueUpdate } from '../models/ProcessValueUpdate';

import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

@Injectable({
  providedIn: 'root',
})
export class DefaultService {

    constructor(public readonly http: HttpClient) {}

    /**
     * Get Unit
     * @param id 
     * @returns ProcessUnit Successful Response
     * @throws ApiError
     */
    public getUnitProcessUnitIdGet(
id: number,
): Observable<ProcessUnit> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/process_unit/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Units
     * @returns ProcessUnit Successful Response
     * @throws ApiError
     */
    public getUnitsProcessUnitsGet(): Observable<Array<ProcessUnit>> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/process_units',
        });
    }

    /**
     * Get Batch
     * @param id 
     * @returns BatchJob Successful Response
     * @throws ApiError
     */
    public getBatchBatchJobIdGet(
id: number,
): Observable<BatchJob> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/batch_job/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Process Values
     * @param id 
     * @returns ProcessValue Successful Response
     * @throws ApiError
     */
    public getProcessValuesProcessUnitIdProcessValuesGet(
id: number,
): Observable<Array<ProcessValue>> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/process_unit/{id}/process_values',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Set Process Value
     * @param id 
     * @param requestBody 
     * @returns any Successful Response
     * @throws ApiError
     */
    public setProcessValueProcessUnitIdProcessValuePost(
id: number,
requestBody: ProcessValueUpdate,
): Observable<any> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/process_unit/{id}/process_value',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
