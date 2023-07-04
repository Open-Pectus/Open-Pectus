/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProcessValueType } from './ProcessValueType';

export type ProcessValueCommandValue = {
    value?: (string | number);
    value_unit?: string;
    valid_value_units?: Array<string>;
    value_type: ProcessValueType;
};
