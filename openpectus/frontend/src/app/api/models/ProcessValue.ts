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
    value_type: ProcessValueType;
    writable: boolean;
    options?: Array<string>;
};
