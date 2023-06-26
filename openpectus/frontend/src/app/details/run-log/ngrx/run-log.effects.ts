import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { map, of, switchMap } from 'rxjs';
import { ProcessUnitService } from '../../../api';
import { selectRouteParam } from '../../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../../details-routing-url-parts';
import { RunLogActions } from './run-log.actions';

@Injectable()
export class RunLogEffects {
  fetchRunLogWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(RunLogActions.runLogComponentInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getRunLog(unitId).pipe(
        map(runLog => RunLogActions.runLogFetched({runLog})),
      );
    }),
  ));

  constructor(private actions: Actions, private store: Store, private processUnitService: ProcessUnitService) {}
}
