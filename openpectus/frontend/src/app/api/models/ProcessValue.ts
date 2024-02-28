/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProcessValueCommand } from './ProcessValueCommand';
import type { ProcessValueType } from './ProcessValueType';
import type { TagDirection } from './TagDirection';

/**
 * Represents a process value. 
 */
export type ProcessValue = {
    name: string;
    value?: (number | string);
    value_unit?: string;
    value_type: ProcessValueType;
    commands?: Array<ProcessValueCommand>;
    direction: TagDirection;
};
