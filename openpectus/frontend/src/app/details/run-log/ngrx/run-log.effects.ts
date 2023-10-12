import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { delay, filter, map, of, switchMap } from 'rxjs';
import { BatchJobService, ProcessUnitService } from '../../../api';
import { DetailsSelectors } from '../../ngrx/details.selectors';
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
    ofType(RunLogActions.runLogComponentInitializedForUnit, RunLogActions.runLogPolledForUnit),
    delay(1000),
    concatLatestFrom(() => this.store.select(DetailsSelectors.shouldPoll)),
    filter(([_, shouldPoll]) => shouldPoll),
    switchMap(([{unitId}]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getRunLog(unitId).pipe(
        map(runLog => RunLogActions.runLogPolledForUnit({runLog, unitId})),
      );
    }),
  ));

  constructor(private actions: Actions, private store: Store,
              private processUnitService: ProcessUnitService,
              private batchJobService: BatchJobService) {}
}
