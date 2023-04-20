/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InProgress } from './InProgress';
import type { NotOnline } from './NotOnline';
import type { Ready } from './Ready';

/**
 * Represents a process unit. 
 */
export type ProcessUnit = {
    id: number;
    name: string;
    state: (Ready | InProgress | NotOnline);
    location?: string;
    runtime_msec?: number;
};
