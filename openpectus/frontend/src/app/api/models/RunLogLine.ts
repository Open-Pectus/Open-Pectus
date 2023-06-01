/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ExecutableCommand } from './ExecutableCommand';

export type RunLogLine = {
    command: ExecutableCommand;
    start: number;
    end: number;
};
