import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { map, mergeMap, of, switchMap, takeUntil } from 'rxjs';
import { ProcessUnitService, RecentRunsService } from '../../../api';
import { PubSubService } from '../../../shared/pub-sub.service';
import { ErrorLogActions } from './error-log.actions';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class ErrorLogEffects {
  fetchErrorLogWhenComponentInitializedForUnit = createEffect(() => this.actions.pipe(
    ofType(ErrorLogActions.errorLogComponentInitializedForUnit),
    switchMap(({unitId}) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getErrorLog(unitId).pipe(
        map(errorLog => ErrorLogActions.errorLogFetched({errorLog})),
      );
    }),
  ));

  fetchErrorLogWhenComponentInitializedForRecentRun = createEffect(() => this.actions.pipe(
    ofType(ErrorLogActions.errorLogComponentInitializedForRecentRun),
    switchMap(({recentRunId}) => {
      if(recentRunId === undefined) return of();
      return this.recentRunsService.getRecentRunErrorLog(recentRunId).pipe(
        map(errorLog => ErrorLogActions.errorLogFetched({errorLog})),
      );
    }),
  ));

  subscribeForUpdatesFromBackend = createEffect(() => this.actions.pipe(
    ofType(ErrorLogActions.errorLogComponentInitializedForUnit),
    mergeMap(({unitId}) => {
      return this.pubSubService.subscribeErrorLog(unitId).pipe(
        takeUntil(this.actions.pipe(ofType(ErrorLogActions.errorLogComponentDestroyed))),
        map(_ => ErrorLogActions.errorLogUpdatedOnBackend({unitId})),
      );
    }),
  ));

  fetchOnUpdateFromBackend = createEffect(() => this.actions.pipe(
    ofType(ErrorLogActions.errorLogUpdatedOnBackend),
    mergeMap(({unitId}) => {
      return this.processUnitService.getErrorLog(unitId).pipe(
        map(errorLog => ErrorLogActions.errorLogFetched({errorLog})),
      );
    }),
  ));

  constructor(private actions: Actions,
              private processUnitService: ProcessUnitService,
              private recentRunsService: RecentRunsService,
              private pubSubService: PubSubService) {}
}
