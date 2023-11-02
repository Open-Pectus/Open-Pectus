import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { delay, filter, map, of, switchMap } from 'rxjs';
import { BatchJobService, ProcessUnitService } from '../../../api';
import { selectRouteParam } from '../../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../../details-routing-url-parts';
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


  forceRunLogLineWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(RunLogActions.forceLineButtonClicked),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([{lineId}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.forceRunLogLine(unitId, lineId);
    }),
  ), {dispatch: false});

  cancelRunLogLineWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(RunLogActions.cancelLineButtonClicked),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([{lineId}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.cancelRunLogLine(unitId, lineId);
    }),
  ), {dispatch: false});

  constructor(private actions: Actions, private store: Store,
              private processUnitService: ProcessUnitService,
              private batchJobService: BatchJobService) {}
}
