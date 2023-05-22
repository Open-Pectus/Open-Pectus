import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { map, switchMap } from 'rxjs';
import { ProcessUnitService } from '../api';
import { AppActions } from './app.actions';

@Injectable()
export class AppEffects {
  loadProcessUnitsOnPageInitialization = createEffect(() => this.actions.pipe(
    ofType(AppActions.pageInitialized),
    switchMap(() => {
      return this.processUnitService.processUnitGetUnits().pipe(map(processUnits => AppActions.processUnitsLoaded({processUnits})));
    }),
  ));

  constructor(private actions: Actions, private processUnitService: ProcessUnitService) {}


}
