/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';

import type { CommandExample } from '../models/CommandExample';
import type { ExecutableCommand } from '../models/ExecutableCommand';
import type { ProcessDiagram } from '../models/ProcessDiagram';
import type { ProcessUnit } from '../models/ProcessUnit';
import type { ProcessValue } from '../models/ProcessValue';
import type { RunLog } from '../models/RunLog';

import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

@Injectable({
  providedIn: 'root',
})
export class ProcessUnitService {

    constructor(public readonly http: HttpClient) {}

    /**
     * Get Unit
     * @param unitId 
     * @returns ProcessUnit Successful Response
     * @throws ApiError
     */
    public getUnit(
unitId: string,
): Observable<ProcessUnit> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}',
            path: {
                'unit_id': unitId,
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
    public getUnits(): Observable<Array<ProcessUnit>> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_units',
        });
    }

    /**
     * Get Process Values
     * @param unitId 
     * @returns ProcessValue Successful Response
     * @throws ApiError
     */
    public getProcessValues(
unitId: string,
): Observable<Array<ProcessValue>> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/process_values',
            path: {
                'unit_id': unitId,
            },
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
    public executeCommand(
unitId: string,
requestBody: ExecutableCommand,
): Observable<any> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/process_unit/{unit_id}/execute_command',
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
    public getProcessDiagram(
unitId: string,
): Observable<ProcessDiagram> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/process_diagram',
            path: {
                'unit_id': unitId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Command Examples
     * @param unitId 
     * @returns CommandExample Successful Response
     * @throws ApiError
     */
    public getCommandExamples(
unitId: string,
): Observable<Array<CommandExample>> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/command_examples',
            path: {
                'unit_id': unitId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Run Log
     * @param unitId 
     * @returns RunLog Successful Response
     * @throws ApiError
     */
    public getRunLog(
unitId: string,
): Observable<RunLog> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/run_log',
            path: {
                'unit_id': unitId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Method
     * @param unitId 
     * @returns string Successful Response
     * @throws ApiError
     */
    public getMethod(
unitId: string,
): Observable<string> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/method',
            path: {
                'unit_id': unitId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
