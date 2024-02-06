/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

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
    contributors?: Array<string>;
};
