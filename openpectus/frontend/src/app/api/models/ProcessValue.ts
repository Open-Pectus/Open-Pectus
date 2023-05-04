/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProcessValueType } from './ProcessValueType';

/**
 * Represents a process value. 
 */
export type ProcessValue = {
    name: string;
    value?: (string | number);
    value_unit?: string;
    valid_value_units?: Array<string>;
    value_type: ProcessValueType;
    writable: boolean;
    options?: Array<string>;
};
