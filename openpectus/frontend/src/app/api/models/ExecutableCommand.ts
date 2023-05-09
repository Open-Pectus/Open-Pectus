/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CommandSource } from './CommandSource';

export type ExecutableCommand = {
    command: string;
    source: CommandSource;
    name?: string;
};
