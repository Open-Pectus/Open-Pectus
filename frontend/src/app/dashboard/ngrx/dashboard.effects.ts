import { Injectable, inject } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { map, switchMap } from 'rxjs';
import { RecentRunsService } from '../../api';
import { DashboardActions } from './dashboard.actions';

@Injectable()
export class DashboardEffects {
  private actions = inject(Actions);
  private recentRunsService = inject(RecentRunsService);

  loadRecentRunsOnComponentInitialization = createEffect(() => this.actions.pipe(
    ofType(DashboardActions.recentRunsInitialized),
    switchMap(() => {
      return this.recentRunsService.getRecentRuns().pipe(
        map(recentRuns => DashboardActions.recentRunsLoaded({recentRuns})));
    }),
  ));
}
