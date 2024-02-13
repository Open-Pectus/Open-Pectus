/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';

import type { CommandExample } from '../models/CommandExample';
import type { ControlState } from '../models/ControlState';
import type { ErrorLog } from '../models/ErrorLog';
import type { ExecutableCommand } from '../models/ExecutableCommand';
import type { Method } from '../models/Method';
import type { MethodAndState } from '../models/MethodAndState';
import type { PlotConfiguration } from '../models/PlotConfiguration';
import type { PlotLog } from '../models/PlotLog';
import type { ProcessDiagram } from '../models/ProcessDiagram';
import type { ProcessUnit } from '../models/ProcessUnit';
import type { ProcessValue } from '../models/ProcessValue';
import type { RunLog } from '../models/RunLog';
import type { SystemStateEnum } from '../models/SystemStateEnum';

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
     * @param engineId 
     * @returns ProcessValue Successful Response
     * @throws ApiError
     */
    public getProcessValues(
engineId: string,
): Observable<Array<ProcessValue>> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{engine_id}/process_values',
            path: {
                'engine_id': engineId,
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
     * Get Method And State
     * @param unitId 
     * @returns MethodAndState Successful Response
     * @throws ApiError
     */
    public getMethodAndState(
unitId: string,
): Observable<MethodAndState> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/method-and-state',
            path: {
                'unit_id': unitId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Save Method
     * @param unitId 
     * @param requestBody 
     * @returns any Successful Response
     * @throws ApiError
     */
    public saveMethod(
unitId: string,
requestBody: Method,
): Observable<any> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/process_unit/{unit_id}/method',
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
     * Get Plot Configuration
     * @param unitId 
     * @returns PlotConfiguration Successful Response
     * @throws ApiError
     */
    public getPlotConfiguration(
unitId: string,
): Observable<PlotConfiguration> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/plot_configuration',
            path: {
                'unit_id': unitId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Plot Log
     * @param unitId 
     * @returns PlotLog Successful Response
     * @throws ApiError
     */
    public getPlotLog(
unitId: string,
): Observable<PlotLog> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/plot_log',
            path: {
                'unit_id': unitId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Control State
     * @param unitId 
     * @returns ControlState Successful Response
     * @throws ApiError
     */
    public getControlState(
unitId: string,
): Observable<ControlState> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/control_state',
            path: {
                'unit_id': unitId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Error Log
     * @param unitId 
     * @returns ErrorLog Successful Response
     * @throws ApiError
     */
    public getErrorLog(
unitId: string,
): Observable<ErrorLog> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/error_log',
            path: {
                'unit_id': unitId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Force Run Log Line
     * @param unitId 
     * @param lineId 
     * @returns any Successful Response
     * @throws ApiError
     */
    public forceRunLogLine(
unitId: string,
lineId: string,
): Observable<any> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/process_unit/{unit_id}/run_log/force_line/{line_id}',
            path: {
                'unit_id': unitId,
                'line_id': lineId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Cancel Run Log Line
     * @param unitId 
     * @param lineId 
     * @returns any Successful Response
     * @throws ApiError
     */
    public cancelRunLogLine(
unitId: string,
lineId: string,
): Observable<any> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/process_unit/{unit_id}/run_log/cancel_line/{line_id}',
            path: {
                'unit_id': unitId,
                'line_id': lineId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Expose System State Enum
     * @returns SystemStateEnum Successful Response
     * @throws ApiError
     */
    public exposeSystemStateEnum(): Observable<SystemStateEnum> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_units/system_state_enum',
        });
    }

}
