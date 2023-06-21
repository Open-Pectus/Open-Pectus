/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ExecutableCommand } from './ExecutableCommand';
import type { ProcessValue } from './ProcessValue';

export type RunLogLine = {
    command: ExecutableCommand;
    start: string;
    end?: string;
    progress?: number;
    start_values: Array<ProcessValue>;
    end_values: Array<ProcessValue>;
};
