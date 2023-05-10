/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';

import type { BatchJob } from '../models/BatchJob';
import type { ExecutableCommand } from '../models/ExecutableCommand';
import type { ProcessDiagram } from '../models/ProcessDiagram';
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
     * Get Recent Batch Jobs
     * @returns BatchJob Successful Response
     * @throws ApiError
     */
    public getRecentBatchJobsRecentBatchJobsGet(): Observable<Array<BatchJob>> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/recent_batch_jobs',
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
     * @param unitId 
     * @param requestBody 
     * @returns any Successful Response
     * @throws ApiError
     */
    public setProcessValueProcessUnitUnitIdProcessValuePost(
unitId: number,
requestBody: ProcessValueUpdate,
): Observable<any> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/process_unit/{unit_id}/process_value',
            path: {
                'unit_id': unitId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Execute Command
     * @param unitId 
     * @param requestBody 
     * @returns any Successful Response
     * @throws ApiError
     */
    public executeCommandProcessUnitUnitIdExecuteCommandPost(
unitId: number,
requestBody: ExecutableCommand,
): Observable<any> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/process_unit/{unit_id}/execute_command',
            path: {
                'unit_id': unitId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Process Diagram
     * @param unitId 
     * @returns ProcessDiagram Successful Response
     * @throws ApiError
     */
    public getProcessDiagramProcessUnitUnitIdProcessDiagramGet(
unitId: number,
): Observable<ProcessDiagram> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/process_unit/{unit_id}/process_diagram',
            path: {
                'unit_id': unitId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
