/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Error } from './Error';
import type { InProgress } from './InProgress';
import type { NotOnline } from './NotOnline';
import type { Ready } from './Ready';
import type { UserRole } from './UserRole';

/**
 * Represents a process unit. 
 */
export type ProcessUnit = {
    id: string;
    name: string;
    state: (Ready | Error | InProgress | NotOnline);
    location?: string;
    runtime_msec?: number;
    current_user_role: UserRole;
};
