/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProcessValueCommandChoiceValue } from './ProcessValueCommandChoiceValue';
import type { ProcessValueCommandFreeTextValue } from './ProcessValueCommandFreeTextValue';
import type { ProcessValueCommandNumberValue } from './ProcessValueCommandNumberValue';

export type ProcessValueCommand = {
    name: string;
    command: string;
    disabled?: boolean;
    value?: (ProcessValueCommandNumberValue | ProcessValueCommandFreeTextValue | ProcessValueCommandChoiceValue);
};
