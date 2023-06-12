/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ExecutableCommand } from './ExecutableCommand';

export type RunLogLine = {
    command: ExecutableCommand;
    start: string;
    end: string;
    additional_values: Array<(string | number)>;
};
