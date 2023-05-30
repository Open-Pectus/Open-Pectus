import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { map, switchMap } from 'rxjs';
import { BatchJobService } from '../../api';
import { DashboardActions } from './dashboard.actions';

@Injectable()
export class DashboardEffects {
  loadRecentBatchJobsOnComponentInitialization = createEffect(() => this.actions.pipe(
    ofType(DashboardActions.recentBatchJobsInitialized),
    switchMap(() => {
      return this.batchJobService.getRecentBatchJobs().pipe(
        map(recentBatchJobs => DashboardActions.recentBatchJobsLoaded({recentBatchJobs})));
    }),
  ));

  constructor(private actions: Actions, private batchJobService: BatchJobService) {}
}
