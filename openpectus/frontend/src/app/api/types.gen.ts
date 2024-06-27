// This file is auto-generated by @hey-api/openapi-ts

export type AuthConfig = {
    use_auth: boolean;
    authority_url?: string;
    client_id?: string;
};

export type CommandExample = {
    name: string;
    example: string;
};

/**
 * An enumeration.
 */
export type CommandSource = 'process_value' | 'manually_entered' | 'unit_button' | 'method';

export type ControlState = {
    is_running: boolean;
    is_holding: boolean;
    is_paused: boolean;
};

export type Error = {
    state: 'error';
};

export type state = 'error';

export type ErrorLog = {
    entries: Array<ErrorLogEntry>;
};

export type ErrorLogEntry = {
    message: string;
    created_time: string;
    severity: ErrorLogSeverity;
};

/**
 * An enumeration.
 */
export type ErrorLogSeverity = 'warning' | 'error';

export type ExecutableCommand = {
    command_id?: string;
    command: string;
    source: CommandSource;
    name?: string;
    value?: ProcessValueCommandNumberValue | ProcessValueCommandFreeTextValue | ProcessValueCommandChoiceValue;
};

export type HTTPValidationError = {
    detail?: Array<ValidationError>;
};

export type InProgress = {
    state: 'in_progress';
    progress_pct: number;
};

export type state2 = 'in_progress';

export type Method = {
    lines: Array<MethodLine>;
};

export type MethodAndState = {
    method: Method;
    state: MethodState;
};

export type MethodLine = {
    id: string;
    content: string;
};

export type MethodState = {
    started_line_ids: Array<(string)>;
    executed_line_ids: Array<(string)>;
    injected_line_ids: Array<(string)>;
};

export type NotOnline = {
    state: 'not_online';
    last_seen_date: string;
};

export type state3 = 'not_online';

export type PlotAxis = {
    label: string;
    process_value_names: Array<(string)>;
    y_max: number;
    y_min: number;
    color: string;
};

export type PlotColorRegion = {
    process_value_name: string;
    value_color_map: {
        [key: string]: (string);
    };
};

export type PlotConfiguration = {
    process_value_names_to_annotate: Array<(string)>;
    color_regions: Array<PlotColorRegion>;
    sub_plots: Array<SubPlot>;
    x_axis_process_value_names: Array<(string)>;
};

export type PlotLog = {
    entries: {
        [key: string]: PlotLogEntry;
    };
};

export type PlotLogEntry = {
    name: string;
    values: Array<PlotLogEntryValue>;
    value_unit?: string;
    value_type: ProcessValueType;
};

export type PlotLogEntryValue = {
    value?: number | string;
    tick_time: number;
};

export type ProcessDiagram = {
    svg: string;
};

/**
 * Represents a process unit.
 */
export type ProcessUnit = {
    id: string;
    name: string;
    state: Ready | Error | InProgress | NotOnline;
    location?: string;
    runtime_msec?: number;
    current_user_role: UserRole;
};

/**
 * Represents a process value.
 */
export type ProcessValue = {
    name: string;
    value?: number | string;
    value_unit?: string;
    value_type: ProcessValueType;
    commands?: Array<ProcessValueCommand>;
    direction: TagDirection;
};

export type ProcessValueCommand = {
    command_id?: string;
    name: string;
    command: string;
    disabled?: boolean;
    value?: ProcessValueCommandNumberValue | ProcessValueCommandFreeTextValue | ProcessValueCommandChoiceValue;
};

export type ProcessValueCommandChoiceValue = {
    value: string;
    value_type: 'choice';
    options: Array<(string)>;
};

export type value_type = 'choice';

export type ProcessValueCommandFreeTextValue = {
    value: string;
    value_type: 'string';
};

export type value_type2 = 'string';

export type ProcessValueCommandNumberValue = {
    value: number;
    value_unit?: string;
    valid_value_units?: Array<(string)>;
    value_type: 'int' | 'float';
};

/**
 * An enumeration.
 */
export type ProcessValueType = 'string' | 'float' | 'int' | 'choice' | 'none';

/**
 * An enumeration.
 */
export type PubSubTopic = 'run_log' | 'method' | 'control_state' | 'error_log' | 'process_units';

export type Ready = {
    state: 'ready';
};

export type state4 = 'ready';

/**
 * Represents a historical run of a process unit.
 */
export type RecentRun = {
    id: string;
    engine_id: string;
    run_id: string;
    started_date: string;
    completed_date: string;
    engine_computer_name: string;
    engine_version: string;
    engine_hardware_str: string;
    aggregator_computer_name: string;
    aggregator_version: string;
    contributors?: Array<(string)>;
};

export type RecentRunCsv = {
    filename: string;
    csv_content: string;
};

export type RunLog = {
    lines: Array<RunLogLine>;
};

export type RunLogLine = {
    id: string;
    command: ExecutableCommand;
    start: string;
    end?: string;
    progress?: number;
    start_values: Array<ProcessValue>;
    end_values: Array<ProcessValue>;
    forcible?: boolean;
    cancellable?: boolean;
    forced?: boolean;
    cancelled?: boolean;
};

export type SubPlot = {
    axes: Array<PlotAxis>;
    ratio: number;
};

/**
 * An enumeration.
 */
export type SystemStateEnum = 'Running' | 'Paused' | 'Holding' | 'Waiting' | 'Stopped' | 'Restarting';

/**
 * Specifies whether a tag is read from or written to hardware and whether is can be changed in UI.
 *
 * Direction of the tag is in relation to the physical IO. Sensors are regarded as inputs and
 * actuators as outputs. Derived values are regarded as NA.
 */
export type TagDirection = 'input' | 'output' | 'na' | 'unspecified';

/**
 * An enumeration.
 */
export type UserRole = 'viewer' | 'admin';

export type ValidationError = {
    loc: Array<(string | number)>;
    msg: string;
    type: string;
};

export type GetUnitData = {
    unitId: string;
};

export type GetUnitResponse = ProcessUnit;

export type GetUnitsResponse = Array<ProcessUnit>;

export type GetProcessValuesData = {
    engineId: string;
};

export type GetProcessValuesResponse = Array<ProcessValue>;

export type GetAllProcessValuesData = {
    engineId: string;
};

export type GetAllProcessValuesResponse = Array<ProcessValue>;

export type ExecuteCommandData = {
    requestBody: ExecutableCommand;
    unitId: string;
};

export type ExecuteCommandResponse = unknown;

export type GetProcessDiagramData = {
    unitId: string;
};

export type GetProcessDiagramResponse = ProcessDiagram;

export type GetCommandExamplesData = {
    unitId: string;
};

export type GetCommandExamplesResponse = Array<CommandExample>;

export type GetRunLogData = {
    unitId: string;
};

export type GetRunLogResponse = RunLog;

export type GetMethodAndStateData = {
    unitId: string;
};

export type GetMethodAndStateResponse = MethodAndState;

export type SaveMethodData = {
    requestBody: Method;
    unitId: string;
};

export type SaveMethodResponse = unknown;

export type GetPlotConfigurationData = {
    unitId: string;
};

export type GetPlotConfigurationResponse = PlotConfiguration;

export type GetPlotLogData = {
    unitId: string;
};

export type GetPlotLogResponse = PlotLog;

export type GetControlStateData = {
    unitId: string;
};

export type GetControlStateResponse = ControlState;

export type GetErrorLogData = {
    unitId: string;
};

export type GetErrorLogResponse = ErrorLog;

export type ForceRunLogLineData = {
    lineId: string;
    unitId: string;
};

export type ForceRunLogLineResponse = unknown;

export type CancelRunLogLineData = {
    lineId: string;
    unitId: string;
};

export type CancelRunLogLineResponse = unknown;

export type ExposeSystemStateEnumResponse = SystemStateEnum;

export type GetRecentRunsResponse = Array<RecentRun>;

export type GetRecentRunData = {
    runId: string;
};

export type GetRecentRunResponse = RecentRun;

export type GetRecentRunMethodAndStateData = {
    runId: string;
};

export type GetRecentRunMethodAndStateResponse = MethodAndState;

export type GetRecentRunRunLogData = {
    runId: string;
};

export type GetRecentRunRunLogResponse = RunLog;

export type GetRecentRunPlotConfigurationData = {
    runId: string;
};

export type GetRecentRunPlotConfigurationResponse = PlotConfiguration;

export type GetRecentRunPlotLogData = {
    runId: string;
};

export type GetRecentRunPlotLogResponse = PlotLog;

export type GetRecentRunCsvJsonData = {
    runId: string;
};

export type GetRecentRunCsvJsonResponse = RecentRunCsv;

export type GetRecentRunErrorLogData = {
    runId: string;
};

export type GetRecentRunErrorLogResponse = ErrorLog;

export type GetRecentRunCsvFileData = {
    id: string;
};

export type GetRecentRunCsvFileResponse = unknown;

export type GetConfigResponse = AuthConfig;

export type PostResponse = unknown;

export type ExposePubsubTopicsData = {
    topic: PubSubTopic;
};

export type ExposePubsubTopicsResponse = unknown;

export type TriggerPublishMswResponse = unknown;

export type $OpenApiTs = {
    '/api/process_unit/{unit_id}': {
        get: {
            req: GetUnitData;
            res: {
                /**
                 * Successful Response
                 */
                200: ProcessUnit;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_units': {
        get: {
            res: {
                /**
                 * Successful Response
                 */
                200: Array<ProcessUnit>;
            };
        };
    };
    '/api/process_unit/{engine_id}/process_values': {
        get: {
            req: GetProcessValuesData;
            res: {
                /**
                 * Successful Response
                 */
                200: Array<ProcessValue>;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{engine_id}/all_process_values': {
        get: {
            req: GetAllProcessValuesData;
            res: {
                /**
                 * Successful Response
                 */
                200: Array<ProcessValue>;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/execute_command': {
        post: {
            req: ExecuteCommandData;
            res: {
                /**
                 * Successful Response
                 */
                200: unknown;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/process_diagram': {
        get: {
            req: GetProcessDiagramData;
            res: {
                /**
                 * Successful Response
                 */
                200: ProcessDiagram;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/command_examples': {
        get: {
            req: GetCommandExamplesData;
            res: {
                /**
                 * Successful Response
                 */
                200: Array<CommandExample>;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/run_log': {
        get: {
            req: GetRunLogData;
            res: {
                /**
                 * Successful Response
                 */
                200: RunLog;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/method-and-state': {
        get: {
            req: GetMethodAndStateData;
            res: {
                /**
                 * Successful Response
                 */
                200: MethodAndState;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/method': {
        post: {
            req: SaveMethodData;
            res: {
                /**
                 * Successful Response
                 */
                200: unknown;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/plot_configuration': {
        get: {
            req: GetPlotConfigurationData;
            res: {
                /**
                 * Successful Response
                 */
                200: PlotConfiguration;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/plot_log': {
        get: {
            req: GetPlotLogData;
            res: {
                /**
                 * Successful Response
                 */
                200: PlotLog;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/control_state': {
        get: {
            req: GetControlStateData;
            res: {
                /**
                 * Successful Response
                 */
                200: ControlState;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/error_log': {
        get: {
            req: GetErrorLogData;
            res: {
                /**
                 * Successful Response
                 */
                200: ErrorLog;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/run_log/force_line/{line_id}': {
        post: {
            req: ForceRunLogLineData;
            res: {
                /**
                 * Successful Response
                 */
                200: unknown;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_unit/{unit_id}/run_log/cancel_line/{line_id}': {
        post: {
            req: CancelRunLogLineData;
            res: {
                /**
                 * Successful Response
                 */
                200: unknown;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/process_units/system_state_enum': {
        get: {
            res: {
                /**
                 * Successful Response
                 */
                200: SystemStateEnum;
            };
        };
    };
    '/api/recent_runs/': {
        get: {
            res: {
                /**
                 * Successful Response
                 */
                200: Array<RecentRun>;
            };
        };
    };
    '/api/recent_runs/{run_id}': {
        get: {
            req: GetRecentRunData;
            res: {
                /**
                 * Successful Response
                 */
                200: RecentRun;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/recent_runs/{run_id}/method-and-state': {
        get: {
            req: GetRecentRunMethodAndStateData;
            res: {
                /**
                 * Successful Response
                 */
                200: MethodAndState;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/recent_runs/{run_id}/run_log': {
        get: {
            req: GetRecentRunRunLogData;
            res: {
                /**
                 * Successful Response
                 */
                200: RunLog;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/recent_runs/{run_id}/plot_configuration': {
        get: {
            req: GetRecentRunPlotConfigurationData;
            res: {
                /**
                 * Successful Response
                 */
                200: PlotConfiguration;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/recent_runs/{run_id}/plot_log': {
        get: {
            req: GetRecentRunPlotLogData;
            res: {
                /**
                 * Successful Response
                 */
                200: PlotLog;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/recent_runs/{run_id}/csv_json': {
        get: {
            req: GetRecentRunCsvJsonData;
            res: {
                /**
                 * Successful Response
                 */
                200: RecentRunCsv;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/recent_runs/{run_id}/error_log': {
        get: {
            req: GetRecentRunErrorLogData;
            res: {
                /**
                 * Successful Response
                 */
                200: ErrorLog;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/recent_runs/{id}/csv_file': {
        get: {
            req: GetRecentRunCsvFileData;
            res: {
                /**
                 * Successful Response
                 */
                200: unknown;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/auth/config': {
        get: {
            res: {
                /**
                 * Successful Response
                 */
                200: AuthConfig;
            };
        };
    };
    '/engine-rest': {
        post: {
            res: {
                /**
                 * Successful Response
                 */
                200: unknown;
            };
        };
    };
    '/api/expose-pubsub-topics': {
        post: {
            req: ExposePubsubTopicsData;
            res: {
                /**
                 * Successful Response
                 */
                200: unknown;
                /**
                 * Validation Error
                 */
                422: HTTPValidationError;
            };
        };
    };
    '/api/trigger-publish-msw': {
        post: {
            res: {
                /**
                 * Successful Response
                 */
                200: unknown;
            };
        };
    };
};