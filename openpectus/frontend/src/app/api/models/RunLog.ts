/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RunLogColumn } from './RunLogColumn';
import type { RunLogLine } from './RunLogLine';

export type RunLog = {
    additional_columns: Array<RunLogColumn>;
    lines: Array<RunLogLine>;
};
