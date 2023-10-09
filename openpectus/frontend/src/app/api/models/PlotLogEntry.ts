/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { PlotLogEntryValue } from './PlotLogEntryValue';
import type { ProcessValueType } from './ProcessValueType';

export type PlotLogEntry = {
    name: string;
    values: Array<PlotLogEntryValue>;
    value_unit?: string;
    value_type: ProcessValueType;
};
