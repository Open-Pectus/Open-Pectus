/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Method } from './Method';

/**
 * Represents a historical run of a process unit. 
 */
export type RecentRun = {
    id: string;
    engine_id: string;
    run_id: string;
    started_date: string;
    completed_date: string;
    contributors?: Array<string>;
    method: Method;
};
