/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

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
    state: (Ready | InProgress | NotOnline);
    location?: string;
    runtime_msec?: number;
    current_user_role: UserRole;
};
