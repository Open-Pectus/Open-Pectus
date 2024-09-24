import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { of, switchMap } from 'rxjs';
import { CommandSource, ProcessUnitService } from '../../../api';
import { DetailsSelectors } from '../../ngrx/details.selectors';
import { ProcessValuesActions } from './process-values.actions';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class ProcessValuesEffects {
  executeProcessValueCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(ProcessValuesActions.processValueCommandClicked),
    concatLatestFrom(() => this.store.select(DetailsSelectors.processUnitId)),
    switchMap(([{command}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.executeCommand({unitId, requestBody: {...command, source: CommandSource.PROCESS_VALUE}});
    }),
  ), {dispatch: false});

  constructor(private actions: Actions, private store: Store, private processUnitService: ProcessUnitService) {}
}
