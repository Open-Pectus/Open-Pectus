/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CommandSource } from './CommandSource';
import type { ProcessValueCommandChoiceValue } from './ProcessValueCommandChoiceValue';
import type { ProcessValueCommandFreeTextValue } from './ProcessValueCommandFreeTextValue';
import type { ProcessValueCommandNumberValue } from './ProcessValueCommandNumberValue';

export type ExecutableCommand = {
    command_id?: string;
    command: string;
    source: CommandSource;
    name?: string;
    value?: (ProcessValueCommandNumberValue | ProcessValueCommandFreeTextValue | ProcessValueCommandChoiceValue);
};
