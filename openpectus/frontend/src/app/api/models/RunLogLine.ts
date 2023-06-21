/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ExecutableCommand } from './ExecutableCommand';

export type RunLogLine = {
    command: ExecutableCommand;
    start: string;
    end?: string;
    progress?: number;
    additional_values: Array<(string | number)>;
};
