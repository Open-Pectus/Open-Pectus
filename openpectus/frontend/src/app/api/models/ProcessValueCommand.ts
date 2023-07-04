/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProcessValueCommandValue } from './ProcessValueCommandValue';

export type ProcessValueCommand = {
    name: string;
    command: string;
    disabled?: boolean;
    value?: ProcessValueCommandValue;
};
