import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { map, switchMap } from 'rxjs';
import { DefaultService } from '../api';
import { DashboardActions } from './dashboard.actions';

@Injectable()
export class DashboardEffects {
  loadProcessUnitsOnPageInitialization = createEffect(() => this.actions.pipe(
    ofType(DashboardActions.pageInitialized),
    switchMap(() => {
      return this.apiService.getUnitsProcessUnitsGet().pipe(map(processUnits => DashboardActions.processUnitsLoaded({processUnits})));
    }),
  ));

  loadRecentBatchJobsOnComponentInitialization = createEffect(() => this.actions.pipe(
    ofType(DashboardActions.recentBatchJobsInitialized),
    switchMap(() => {
      return this.apiService.getRecentBatchJobsRecentBatchJobsGet().pipe(
        map(recentBatchJobs => DashboardActions.recentBatchJobsLoaded({recentBatchJobs})));
    }),
  ));

  constructor(private actions: Actions, private apiService: DefaultService) {}
}
