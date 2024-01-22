import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { map, mergeMap, of, switchMap, takeUntil } from 'rxjs';
import { ProcessUnitService, RecentRunsService } from '../../../api';
import { selectRouteParam } from '../../../ngrx/router.selectors';
import { PubSubService } from '../../../shared/pub-sub.service';
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

  fetchRunLogWhenComponentInitializedForRecentRun = createEffect(() => this.actions.pipe(
    ofType(RunLogActions.runLogComponentInitializedForRecentRun),
    switchMap(({recentRunId}) => {
      if(recentRunId === undefined) return of();
      return this.recentRunsService.getRecentRunRunLog(recentRunId).pipe(
        map(runLog => RunLogActions.runLogFetched({runLog})),
      );
    }),
  ));

  subscribeForUpdatesFromBackend = createEffect(() => this.actions.pipe(
    ofType(RunLogActions.runLogComponentInitializedForUnit),
    mergeMap(({unitId}) => {
      return this.pubSubService.subscribeRunLog(unitId).pipe(
        takeUntil(this.actions.pipe(ofType(RunLogActions.runLogComponentDestroyed))),
        map(_ => RunLogActions.runLogUpdatedOnBackend({unitId})),
      );
    }),
  ));

  fetchOnUpdateFromBackend = createEffect(() => this.actions.pipe(
    ofType(RunLogActions.runLogUpdatedOnBackend),
    mergeMap(({unitId}) => {
      return this.processUnitService.getRunLog(unitId).pipe(
        map(runLog => RunLogActions.runLogFetched({runLog})),
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
              private recentRunsService: RecentRunsService,
              private pubSubService: PubSubService) {}
}
