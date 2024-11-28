// This file is auto-generated by @hey-api/openapi-ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';
import { OpenAPI } from './core/OpenAPI';
import { request as __request } from './core/request';
import type { GetUnitData, GetUnitResponse, GetUnitsData, GetUnitsResponse, GetProcessValuesData, GetProcessValuesResponse, GetAllProcessValuesData, GetAllProcessValuesResponse, ExecuteCommandData, ExecuteCommandResponse, GetProcessDiagramData, GetProcessDiagramResponse, GetCommandExamplesData, GetCommandExamplesResponse, GetRunLogData, GetRunLogResponse, GetMethodAndStateData, GetMethodAndStateResponse, SaveMethodData, SaveMethodResponse, GetPlotConfigurationData, GetPlotConfigurationResponse, GetPlotLogData, GetPlotLogResponse, GetControlStateData, GetControlStateResponse, GetErrorLogData, GetErrorLogResponse, ForceRunLogLineData, ForceRunLogLineResponse, CancelRunLogLineData, CancelRunLogLineResponse, ExposeSystemStateEnumData, ExposeSystemStateEnumResponse, GetRecentRunsData, GetRecentRunsResponse, GetRecentRunData, GetRecentRunResponse, GetRecentRunMethodAndStateData, GetRecentRunMethodAndStateResponse, GetRecentRunRunLogData, GetRecentRunRunLogResponse, GetRecentRunPlotConfigurationData, GetRecentRunPlotConfigurationResponse, GetRecentRunPlotLogData, GetRecentRunPlotLogResponse, GetRecentRunCsvJsonData, GetRecentRunCsvJsonResponse, GetRecentRunErrorLogData, GetRecentRunErrorLogResponse, GetRecentRunCsvFileData, GetRecentRunCsvFileResponse, GetConfigResponse, PostResponse, ExposePubsubTopicsData, ExposePubsubTopicsResponse, TriggerPublishMswResponse, GetVersionResponse, GetBuildNumberResponse, GetBuildInfoResponse } from './types.gen';

@Injectable({
    providedIn: 'root'
})
export class ProcessUnitService {
    constructor(public readonly http: HttpClient) { }
    
    /**
     * Get Unit
     * @param data The data for the request.
     * @param data.unitId
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Units
     * @param data The data for the request.
     * @param data.xIdentity
     * @returns ProcessUnit Successful Response
     * @throws ApiError
     */
    public getUnits(data: GetUnitsData = {}): Observable<GetUnitsResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_units',
            headers: {
                'x-identity': data.xIdentity
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Process Values
     * @param data The data for the request.
     * @param data.engineId
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
     * @returns AggregatedErrorLog Successful Response
     * @throws ApiError
     */
    public getErrorLog(data: GetErrorLogData): Observable<GetErrorLogResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_unit/{unit_id}/error_log',
            path: {
                unit_id: data.unitId
            },
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Expose System State Enum
     * @param data The data for the request.
     * @param data.xIdentity
     * @returns SystemStateEnum Successful Response
     * @throws ApiError
     */
    public exposeSystemStateEnum(data: ExposeSystemStateEnumData = {}): Observable<ExposeSystemStateEnumResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/process_units/system_state_enum',
            headers: {
                'x-identity': data.xIdentity
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
export class RecentRunsService {
    constructor(public readonly http: HttpClient) { }
    
    /**
     * Get Recent Runs
     * @param data The data for the request.
     * @param data.xIdentity
     * @returns RecentRun Successful Response
     * @throws ApiError
     */
    public getRecentRuns(data: GetRecentRunsData = {}): Observable<GetRecentRunsResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/',
            headers: {
                'x-identity': data.xIdentity
            },
            errors: {
                422: 'Validation Error'
            }
        });
    }
    
    /**
     * Get Recent Run
     * @param data The data for the request.
     * @param data.runId
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
     * @returns AggregatedErrorLog Successful Response
     * @throws ApiError
     */
    public getRecentRunErrorLog(data: GetRecentRunErrorLogData): Observable<GetRecentRunErrorLogResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/recent_runs/{run_id}/error_log',
            path: {
                run_id: data.runId
            },
            headers: {
                'x-identity': data.xIdentity
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
     * @param data.xIdentity
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
            headers: {
                'x-identity': data.xIdentity
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

@Injectable({
    providedIn: 'root'
})
export class VersionService {
    constructor(public readonly http: HttpClient) { }
    
    /**
     * Get Version
     * @returns unknown Successful Response
     * @throws ApiError
     */
    public getVersion(): Observable<GetVersionResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/version'
        });
    }
    
    /**
     * Get Build Number
     * @returns unknown Successful Response
     * @throws ApiError
     */
    public getBuildNumber(): Observable<GetBuildNumberResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/build_number'
        });
    }
    
    /**
     * Get Build Info
     * @returns BuildInfo Successful Response
     * @throws ApiError
     */
    public getBuildInfo(): Observable<GetBuildInfoResponse> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/build_info'
        });
    }
    
}