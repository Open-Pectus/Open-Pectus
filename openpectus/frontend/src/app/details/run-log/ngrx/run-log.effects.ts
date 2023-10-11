import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { debounceTime, map, of, switchMap } from 'rxjs';
import { BatchJobService, ProcessUnitService } from '../../../api';
import { selectRouteParam } from '../../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../../details-routing-url-parts';
import { RunLogActions } from './run-log.actions';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class RunLogEffects {
  fetchRunLogWhenComponentInitializedForUnit = createEffect(() => this.actions.pipe(
    ofType(RunLogActions.runLogComponentInitializedForUnit),
    switchMap(({unitId}) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getRunLog(unitId).pipe(
        map(runLog => RunLogActions.runLogFetched({runLog})),
      );
    }),
  ));

  fetchRunLogWhenComponentInitializedForBatchJob = createEffect(() => this.actions.pipe(
    ofType(RunLogActions.runLogComponentInitializedForBatchJob),
    switchMap(({batchJobId}) => {
      if(batchJobId === undefined) return of();
      return this.batchJobService.getBatchJobRunLog(batchJobId).pipe(
        map(runLog => RunLogActions.runLogFetched({runLog})),
      );
    }),
  ));

  // TODO: this should happen via websocket, not polling
  continuouslyPollRunLog = createEffect(() => this.actions.pipe(
    ofType(RunLogActions.runLogFetched),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    debounceTime(1000),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getRunLog(unitId).pipe(
        map(runLog => RunLogActions.runLogFetched({runLog})),
      );
    }),
  ));

  constructor(private actions: Actions, private store: Store,
              private processUnitService: ProcessUnitService,
              private batchJobService: BatchJobService) {}
}
