import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { map, switchMap } from 'rxjs';
import { DefaultService } from '../api';
import { AppActions } from './app.actions';

@Injectable()
export class AppEffects {
  loadProcessUnitsOnPageInitialization = createEffect(() => this.actions.pipe(
    ofType(AppActions.pageInitialized),
    switchMap(() => {
      return this.apiService.getUnitsProcessUnitsGet().pipe(map(processUnits => AppActions.processUnitsLoaded({processUnits})));
    }),
  ));

  constructor(private actions: Actions, private apiService: DefaultService) {}


}
