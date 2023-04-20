/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Represents a current or historical run of a process unit. 
 */
export type BatchJob = {
    id: number;
    unit_id: number;
    unit_name: string;
    completed_date: string;
    contributors?: Array<string>;
};
