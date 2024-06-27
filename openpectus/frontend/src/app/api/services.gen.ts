// This file is auto-generated by @hey-api/openapi-ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';
import { OpenAPI } from './core/OpenAPI';
import { request as __request } from './core/request';
import type { GetUnitData, GetUnitResponse, GetUnitsResponse, GetProcessValuesData, GetProcessValuesResponse, GetAllProcessValuesData, GetAllProcessValuesResponse, ExecuteCommandData, ExecuteCommandResponse, GetProcessDiagramData, GetProcessDiagramResponse, GetCommandExamplesData, GetCommandExamplesResponse, GetRunLogData, GetRunLogResponse, GetMethodAndStateData, GetMethodAndStateResponse, SaveMethodData, SaveMethodResponse, GetPlotConfigurationData, GetPlotConfigurationResponse, GetPlotLogData, GetPlotLogResponse, GetControlStateData, GetControlStateResponse, GetErrorLogData, GetErrorLogResponse, ForceRunLogLineData, ForceRunLogLineResponse, CancelRunLogLineData, CancelRunLogLineResponse, ExposeSystemStateEnumResponse, GetRecentRunsResponse, GetRecentRunData, GetRecentRunResponse, GetRecentRunMethodAndStateData, GetRecentRunMethodAndStateResponse, GetRecentRunRunLogData, GetRecentRunRunLogResponse, GetRecentRunPlotConfigurationData, GetRecentRunPlotConfigurationResponse, GetRecentRunPlotLogData, GetRecentRunPlotLogResponse, GetRecentRunCsvJsonData, GetRecentRunCsvJsonResponse, GetRecentRunErrorLogData, GetRecentRunErrorLogResponse, GetRecentRunCsvFileData, GetRecentRunCsvFileResponse, GetConfigResponse, PostResponse, ExposePubsubTopicsData, ExposePubsubTopicsResponse, TriggerPublishMswResponse } from './types.gen';

@Injectable({
    providedIn: 'root'
})
export class ProcessUnitService {
    constructor(public readonly http: HttpClient) { }
    
    /**
     * Get Unit
     * @param data The data for the request.
     * @param data.unitId
     * @returns ProcessUnit Successful Response
     * @throws ApiError
     */
    public getUnit(data: GetUnitData): Observable<GetUnitResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}',
            path: {
                unit_id: data.unitId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Units
     * @returns ProcessUnit Successful Response
     * @throws ApiError
     */
    public getUnits(): Observable<GetUnitsResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_units'
        });
    }
    
    /**
     * Get Process Values
     * @param data The data for the request.
     * @param data.engineId
     * @returns ProcessValue Successful Response
     * @throws ApiError
     */
    public getProcessValues(data: GetProcessValuesData): Observable<GetProcessValuesResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{engine_id}/process_values',
            path: {
                engine_id: data.engineId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get All Process Values
     * @param data The data for the request.
     * @param data.engineId
     * @returns ProcessValue Successful Response
     * @throws ApiError
     */
    public getAllProcessValues(data: GetAllProcessValuesData): Observable<GetAllProcessValuesResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{engine_id}/all_process_values',
            path: {
                engine_id: data.engineId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Execute Command
     * @param data The data for the request.
     * @param data.unitId
     * @param data.requestBody
     * @returns unknown Successful Response
     * @throws ApiError
     */
    public executeCommand(data: ExecuteCommandData): Observable<ExecuteCommandResponse> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/process_unit/{unit_id}/execute_command',
            path: {
                unit_id: data.unitId
            },
            body: data.requestBody,
            mediaType: 'application/json',
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Process Diagram
     * @param data The data for the request.
     * @param data.unitId
     * @returns ProcessDiagram Successful Response
     * @throws ApiError
     */
    public getProcessDiagram(data: GetProcessDiagramData): Observable<GetProcessDiagramResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/process_diagram',
            path: {
                unit_id: data.unitId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Command Examples
     * @param data The data for the request.
     * @param data.unitId
     * @returns CommandExample Successful Response
     * @throws ApiError
     */
    public getCommandExamples(data: GetCommandExamplesData): Observable<GetCommandExamplesResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/command_examples',
            path: {
                unit_id: data.unitId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Run Log
     * @param data The data for the request.
     * @param data.unitId
     * @returns RunLog Successful Response
     * @throws ApiError
     */
    public getRunLog(data: GetRunLogData): Observable<GetRunLogResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/run_log',
            path: {
                unit_id: data.unitId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Method And State
     * @param data The data for the request.
     * @param data.unitId
     * @returns MethodAndState Successful Response
     * @throws ApiError
     */
    public getMethodAndState(data: GetMethodAndStateData): Observable<GetMethodAndStateResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/method-and-state',
            path: {
                unit_id: data.unitId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Save Method
     * @param data The data for the request.
     * @param data.unitId
     * @param data.requestBody
     * @returns unknown Successful Response
     * @throws ApiError
     */
    public saveMethod(data: SaveMethodData): Observable<SaveMethodResponse> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/process_unit/{unit_id}/method',
            path: {
                unit_id: data.unitId
            },
            body: data.requestBody,
            mediaType: 'application/json',
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Plot Configuration
     * @param data The data for the request.
     * @param data.unitId
     * @returns PlotConfiguration Successful Response
     * @throws ApiError
     */
    public getPlotConfiguration(data: GetPlotConfigurationData): Observable<GetPlotConfigurationResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/plot_configuration',
            path: {
                unit_id: data.unitId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Plot Log
     * @param data The data for the request.
     * @param data.unitId
     * @returns PlotLog Successful Response
     * @throws ApiError
     */
    public getPlotLog(data: GetPlotLogData): Observable<GetPlotLogResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/plot_log',
            path: {
                unit_id: data.unitId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Control State
     * @param data The data for the request.
     * @param data.unitId
     * @returns ControlState Successful Response
     * @throws ApiError
     */
    public getControlState(data: GetControlStateData): Observable<GetControlStateResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/control_state',
            path: {
                unit_id: data.unitId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Error Log
     * @param data The data for the request.
     * @param data.unitId
     * @returns ErrorLog Successful Response
     * @throws ApiError
     */
    public getErrorLog(data: GetErrorLogData): Observable<GetErrorLogResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/error_log',
            path: {
                unit_id: data.unitId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Force Run Log Line
     * @param data The data for the request.
     * @param data.unitId
     * @param data.lineId
     * @returns unknown Successful Response
     * @throws ApiError
     */
    public forceRunLogLine(data: ForceRunLogLineData): Observable<ForceRunLogLineResponse> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/process_unit/{unit_id}/run_log/force_line/{line_id}',
            path: {
                unit_id: data.unitId,
                line_id: data.lineId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Cancel Run Log Line
     * @param data The data for the request.
     * @param data.unitId
     * @param data.lineId
     * @returns unknown Successful Response
     * @throws ApiError
     */
    public cancelRunLogLine(data: CancelRunLogLineData): Observable<CancelRunLogLineResponse> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/process_unit/{unit_id}/run_log/cancel_line/{line_id}',
            path: {
                unit_id: data.unitId,
                line_id: data.lineId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Expose System State Enum
     * @returns SystemStateEnum Successful Response
     * @throws ApiError
     */
    public exposeSystemStateEnum(): Observable<ExposeSystemStateEnumResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_units/system_state_enum'
        });
    }
    
}

@Injectable({
    providedIn: 'root'
})
export class RecentRunsService {
    constructor(public readonly http: HttpClient) { }
    
    /**
     * Get Recent Runs
     * @returns RecentRun Successful Response
     * @throws ApiError
     */
    public getRecentRuns(): Observable<GetRecentRunsResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/'
        });
    }
    
    /**
     * Get Recent Run
     * @param data The data for the request.
     * @param data.runId
     * @returns RecentRun Successful Response
     * @throws ApiError
     */
    public getRecentRun(data: GetRecentRunData): Observable<GetRecentRunResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{run_id}',
            path: {
                run_id: data.runId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Recent Run Method And State
     * @param data The data for the request.
     * @param data.runId
     * @returns MethodAndState Successful Response
     * @throws ApiError
     */
    public getRecentRunMethodAndState(data: GetRecentRunMethodAndStateData): Observable<GetRecentRunMethodAndStateResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{run_id}/method-and-state',
            path: {
                run_id: data.runId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Recent Run Run Log
     * @param data The data for the request.
     * @param data.runId
     * @returns RunLog Successful Response
     * @throws ApiError
     */
    public getRecentRunRunLog(data: GetRecentRunRunLogData): Observable<GetRecentRunRunLogResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{run_id}/run_log',
            path: {
                run_id: data.runId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Recent Run Plot Configuration
     * @param data The data for the request.
     * @param data.runId
     * @returns PlotConfiguration Successful Response
     * @throws ApiError
     */
    public getRecentRunPlotConfiguration(data: GetRecentRunPlotConfigurationData): Observable<GetRecentRunPlotConfigurationResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{run_id}/plot_configuration',
            path: {
                run_id: data.runId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Recent Run Plot Log
     * @param data The data for the request.
     * @param data.runId
     * @returns PlotLog Successful Response
     * @throws ApiError
     */
    public getRecentRunPlotLog(data: GetRecentRunPlotLogData): Observable<GetRecentRunPlotLogResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{run_id}/plot_log',
            path: {
                run_id: data.runId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Recent Run Csv Json
     * @param data The data for the request.
     * @param data.runId
     * @returns RecentRunCsv Successful Response
     * @throws ApiError
     */
    public getRecentRunCsvJson(data: GetRecentRunCsvJsonData): Observable<GetRecentRunCsvJsonResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{run_id}/csv_json',
            path: {
                run_id: data.runId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Recent Run Error Log
     * @param data The data for the request.
     * @param data.runId
     * @returns ErrorLog Successful Response
     * @throws ApiError
     */
    public getRecentRunErrorLog(data: GetRecentRunErrorLogData): Observable<GetRecentRunErrorLogResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{run_id}/error_log',
            path: {
                run_id: data.runId
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Recent Run Csv File
     * @param data The data for the request.
     * @param data.id
     * @returns unknown Successful Response
     * @throws ApiError
     */
    public getRecentRunCsvFile(data: GetRecentRunCsvFileData): Observable<GetRecentRunCsvFileResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{id}/csv_file',
            path: {
                id: data.id
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    constructor(public readonly http: HttpClient) { }
    
    /**
     * Get Config
     * @returns AuthConfig Successful Response
     * @throws ApiError
     */
    public getConfig(): Observable<GetConfigResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/auth/config'
        });
    }
    
}

@Injectable({
    providedIn: 'root'
})
export class AggregatorService {
    constructor(public readonly http: HttpClient) { }
    
    /**
     * Post
     * @returns unknown Successful Response
     * @throws ApiError
     */
    public post(): Observable<PostResponse> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/engine-rest'
        });
    }
    
}

@Injectable({
    providedIn: 'root'
})
export class FrontendPubsubService {
    constructor(public readonly http: HttpClient) { }
    
    /**
     * Expose Pubsub Topics
     * This endpoint is just for exposing the topic enum to frontend via autogeneration
     * @param data The data for the request.
     * @param data.topic
     * @returns unknown Successful Response
     * @throws ApiError
     */
    public exposePubsubTopics(data: ExposePubsubTopicsData): Observable<ExposePubsubTopicsResponse> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/expose-pubsub-topics',
            query: {
                topic: data.topic
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Trigger Publish Msw
     * Publish to all topics that start with 'MSW_'
     * @returns unknown Successful Response
     * @throws ApiError
     */
    public triggerPublishMsw(): Observable<TriggerPublishMswResponse> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/trigger-publish-msw'
        });
    }
    
}