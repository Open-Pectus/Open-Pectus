/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';

import type { MethodAndState } from '../models/MethodAndState';
import type { PlotConfiguration } from '../models/PlotConfiguration';
import type { PlotLog } from '../models/PlotLog';
import type { RecentRun } from '../models/RecentRun';
import type { RecentRunCsv } from '../models/RecentRunCsv';
import type { RunLog } from '../models/RunLog';

import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

@Injectable({
  providedIn: 'root',
})
export class RecentRunsService {

    constructor(public readonly http: HttpClient) {}

    /**
     * Get Recent Runs
     * @returns RecentRun Successful Response
     * @throws ApiError
     */
    public getRecentRuns(): Observable<Array<RecentRun>> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/',
        });
    }

    /**
     * Get Recent Run
     * @param runId 
     * @returns RecentRun Successful Response
     * @throws ApiError
     */
    public getRecentRun(
runId: string,
): Observable<RecentRun> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{run_id}',
            path: {
                'run_id': runId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Recent Run Method And State
     * @param runId 
     * @returns MethodAndState Successful Response
     * @throws ApiError
     */
    public getRecentRunMethodAndState(
runId: string,
): Observable<MethodAndState> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{run_id}/method-and-state',
            path: {
                'run_id': runId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Recent Run Run Log
     * @param id 
     * @returns RunLog Successful Response
     * @throws ApiError
     */
    public getRecentRunRunLog(
id: string,
): Observable<RunLog> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{id}/run_log',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Recent Run Plot Configuration
     * @param id 
     * @returns PlotConfiguration Successful Response
     * @throws ApiError
     */
    public getRecentRunPlotConfiguration(
id: string,
): Observable<PlotConfiguration> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{id}/plot_configuration',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Recent Run Plot Log
     * @param id 
     * @returns PlotLog Successful Response
     * @throws ApiError
     */
    public getRecentRunPlotLog(
id: string,
): Observable<PlotLog> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{id}/plot_log',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Recent Run Csv Json
     * @param id 
     * @returns RecentRunCsv Successful Response
     * @throws ApiError
     */
    public getRecentRunCsvJson(
id: string,
): Observable<RecentRunCsv> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{id}/csv_json',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Recent Run Csv File
     * @param id 
     * @returns any Successful Response
     * @throws ApiError
     */
    public getRecentRunCsvFile(
id: string,
): Observable<any> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{id}/csv_file',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
