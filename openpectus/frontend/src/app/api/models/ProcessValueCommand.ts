/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProcessValueCommandChoiceValue } from './ProcessValueCommandChoiceValue';
import type { ProcessValueCommandFreeTextValue } from './ProcessValueCommandFreeTextValue';
import type { ProcessValueCommandNumberValue } from './ProcessValueCommandNumberValue';

export type ProcessValueCommand = {
    command_id?: string;
    name: string;
    command: string;
    disabled?: boolean;
    value?: (ProcessValueCommandNumberValue | ProcessValueCommandFreeTextValue | ProcessValueCommandChoiceValue);
};
