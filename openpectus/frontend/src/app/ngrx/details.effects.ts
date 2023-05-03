import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { map, of, switchMap } from 'rxjs';
import { DefaultService } from '../api';
import { unitIdParamName } from '../details/details-routing.module';
import { DetailsActions } from './details.actions';
import { DetailsSelectors } from './details.selectors';
import { selectRouteParam } from './router.selectors';

@Injectable()
export class DetailsEffects {
  saveMethodEditorModel = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.methodEditorModelSaveRequested),
    concatLatestFrom(() => this.store.select(DetailsSelectors.methodEditorContent)),
    switchMap(([_, content]) => {
      /* save model to backend */
      alert(`model saved! ${content}`);
      return of(DetailsActions.methodEditorModelSaved());
    }),
  ));

  loadProcessValuesWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processValuesInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(unitIdParamName))),
    switchMap(([_, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      if(isNaN(unitIdAsNumber)) return of(DetailsActions.processValuesFailedToLoad());
      return this.apiService.getProcessValuesProcessUnitIdProcessValuesGet(unitIdAsNumber).pipe(map(processValues => {
        return DetailsActions.processValuesLoaded({processValues});
      }));
    }),
  ));

  constructor(private actions: Actions, private store: Store, private apiService: DefaultService) {}
}
