/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ExecutableCommand } from './ExecutableCommand';
import type { ProcessValue } from './ProcessValue';

export type RunLogLine = {
    id: number;
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
