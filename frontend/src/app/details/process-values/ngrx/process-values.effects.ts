import { Injectable, inject } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { of, switchMap } from 'rxjs';
import { ProcessUnitService } from '../../../api';
import { DetailsSelectors } from '../../ngrx/details.selectors';
import { ProcessValuesActions } from './process-values.actions';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class ProcessValuesEffects {
  private actions = inject(Actions);
  private store = inject(Store);
  private processUnitService = inject(ProcessUnitService);

  executeProcessValueCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(ProcessValuesActions.processValueCommandClicked),
    concatLatestFrom(() => this.store.select(DetailsSelectors.processUnitId)),
    switchMap(([{command}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.executeCommand({unitId, requestBody: {...command, source: 'process_value'}});
    }),
  ), {dispatch: false});
}
