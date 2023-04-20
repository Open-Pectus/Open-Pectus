/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProcessUnitStateEnum } from './ProcessUnitStateEnum';

export type NotOnline = {
    state?: ProcessUnitStateEnum;
    last_seen_date: string;
};
