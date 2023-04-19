import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { map, switchMap } from 'rxjs';
import { DashboardActions } from './dashboard.actions';
import { DefaultService } from '../api';

@Injectable()
export class DashboardEffects {
  loadProcessUnitsOnPageInitialization = createEffect(() => this.actions.pipe(
    ofType(DashboardActions.pageInitialized),
    switchMap(() => {
      return this.apiService.getUnitsProcessUnitsGet().pipe(map(processUnits => DashboardActions.processUnitsLoaded({processUnits})));
    }),
  ));

  constructor(private actions: Actions, private apiService: DefaultService) {}
}
