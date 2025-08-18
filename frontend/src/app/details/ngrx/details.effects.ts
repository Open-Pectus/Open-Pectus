import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { catchError, delay, EMPTY, filter, map, mergeMap, of, switchMap, takeUntil } from 'rxjs';
import { ProcessUnitService, RecentRunsService } from '../../api';
import { AppSelectors } from '../../ngrx/app.selectors';
import { selectRouteParam } from '../../ngrx/router.selectors';
import { PubSubService } from '../../shared/pub-sub.service';
import { DetailsRoutingUrlParts } from '../details-routing-url-parts';
import { DetailsActions } from './details.actions';
import { DetailsSelectors } from './details.selectors';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class DetailsEffects {
  fetchProcessValuesWhenPageInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.unitDetailsInitialized),
    switchMap(({unitId}) => {
      return this.processUnitService.getProcessValues({engineId: unitId}).pipe(
        map(processValues => DetailsActions.processValuesFetched({processValues})),
        catchError(error => of(DetailsActions.processValuesFailedToLoad({error}))),
      );
    }),
  ));

  // TODO: When we introduce websocket pubsub, figure out if it makes sense to push process_value changes through it, or polling is fine.
  continuouslyPollProcessValues = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processValuesFetched),
    delay(1000),
    concatLatestFrom(() => [
      this.store.select(DetailsSelectors.processUnitId),
      this.store.select(DetailsSelectors.allProcessValues),
      this.store.select(DetailsSelectors.shouldPoll),
    ]),
    filter(([_, __, ___, shouldPoll]) => shouldPoll),
    switchMap(([_, unitId, allProcessValues]) => {
      if(unitId === undefined) return of();
      const request = allProcessValues
                      ? this.processUnitService.getAllProcessValues({engineId: unitId})
                      : this.processUnitService.getProcessValues({engineId: unitId});
      return request.pipe(
        map(processValues => DetailsActions.processValuesFetched({processValues})),
        catchError(error => of(DetailsActions.processValuesFailedToLoad({error}))),
      );
    }),
  ));

  fetchControlStateWhenPageInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.unitDetailsInitialized),
    switchMap(({unitId}) => {
      return this.processUnitService.getControlState({unitId}).pipe(
        map(controlState => DetailsActions.controlStateFetched({controlState})),
      );
    }),
  ));


  subscribeForControlStateUpdatesFromBackend = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.unitDetailsInitialized),
    mergeMap(({unitId}) => {
      return this.pubSubService.subscribeControlState(unitId).pipe(
        takeUntil(this.actions.pipe(ofType(DetailsActions.unitDetailsDestroyed))),
        map(_ => DetailsActions.controlStateUpdatedOnBackend({unitId})),
      );
    }),
  ));


  fetchControlStateOnUpdateFromBackend = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.controlStateUpdatedOnBackend),
    mergeMap(({unitId}) => {
      return this.processUnitService.getControlState({unitId}).pipe(
        map(controlState => DetailsActions.controlStateFetched({controlState})),
      );
    }),
  ));

  executeUnitControlCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processUnitCommandButtonClicked),
    concatLatestFrom(() => this.store.select(DetailsSelectors.processUnitId)),
    mergeMap(([{command}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.executeCommand({unitId, requestBody: {command, source: 'unit_button'}});
    }),
  ), {dispatch: false});

  executeManuallyEnteredCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.commandsComponentExecuteClicked),
    concatLatestFrom(() => this.store.select(DetailsSelectors.processUnitId)),
    switchMap(([{command}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.executeCommand({unitId, requestBody: {...command}});
    }),
  ), {dispatch: false});

  fetchProcessDiagramWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processDiagramInitialized),
    concatLatestFrom(() => this.store.select(DetailsSelectors.processUnitId)),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getProcessDiagram({unitId}).pipe(
        map(processDiagram => DetailsActions.processDiagramFetched({processDiagram})),
      );
    }),
  ));

  fetchCommandExamplesWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.commandsComponentInitialized),
    concatLatestFrom(() => this.store.select(DetailsSelectors.processUnitId)),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getCommandExamples({unitId}).pipe(
        map(commandExamples => DetailsActions.commandExamplesFetched({commandExamples})),
      );
    }),
  ));

  fetchRecentRunWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.recentRunDetailsInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.recentRunIdParamName))),
    switchMap(([_, recentRunId]) => {
      if(recentRunId === undefined) return of();
      return this.recentRunsService.getRecentRun({runId: recentRunId}).pipe(
        map(recentRun => DetailsActions.recentRunFetched({recentRun})),
        catchError(error => of(DetailsActions.recentRunFailedToLoad({error}))),
      );
    }),
  ));

  downloadRecentRunCsvWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.recentRunDownloadCsvButtonClicked),
    switchMap(({recentRunId}) => {
      return this.recentRunsService.getRecentRunCsvJson({runId: recentRunId}).pipe(
        map(RecentRunCsv => {
          const link = document.createElement('a');
          link.download = RecentRunCsv.filename;
          link.href = URL.createObjectURL(new Blob([RecentRunCsv.csv_content]));
          link.click();
        }),
      );
    }),
  ), {dispatch: false});

  registerAsActiveUser = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.unitDetailsInitialized),
    concatLatestFrom(() => [
      this.store.select(AppSelectors.authIsEnabled),
      this.store.select(AppSelectors.userId),
    ]),
    mergeMap(([{unitId}, authIsEnabled, userId]) => {
      return this.processUnitService.registerActiveUser({unitId, userId: authIsEnabled ? undefined : userId});
    }),
  ), {dispatch: false});

  unregisterAsActiveUser = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processUnitNavigatedFrom),
    concatLatestFrom(() => [
      this.store.select(AppSelectors.authIsEnabled),
      this.store.select(AppSelectors.userId),
    ]),
    mergeMap(([{oldUnitId}, authIsEnabled, userId]) => {
      if(oldUnitId === undefined) return EMPTY;
      return this.processUnitService.unregisterActiveUser({unitId: oldUnitId, userId: authIsEnabled ? undefined : userId});
    }),
  ), {dispatch: false});

  reregisterAsActiveUser = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processUnitNavigatedFrom),
    concatLatestFrom(() => [
      this.store.select(AppSelectors.authIsEnabled),
      this.store.select(AppSelectors.userId),
    ]),
    mergeMap(([{newUnitId}, authIsEnabled, userId]) => {
      if(newUnitId === undefined) return EMPTY;
      return this.processUnitService.registerActiveUser({unitId: newUnitId, userId: authIsEnabled ? undefined : userId});
    }),
  ), {dispatch: false});

  fetchOtherActiveUsers = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.unitDetailsInitialized, DetailsActions.activeUsersUpdatedOnBackend),
    concatLatestFrom(() => this.store.select(AppSelectors.userId)),
    switchMap(([{unitId}, userId]) => {
      return this.processUnitService.getActiveUsers({unitId}).pipe(
        map(activeUsers => activeUsers.filter(activeUser => activeUser.id !== userId)),
        map(otherActiveUsers => DetailsActions.otherActiveUsersFetched({otherActiveUsers})),
      );
    }),
  ));

  subscribeForActiveUsersUpdatesFromBackend = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.unitDetailsInitialized),
    mergeMap(({unitId}) => {
      return this.pubSubService.subscribeActiveUsers(unitId).pipe(
        takeUntil(this.actions.pipe(ofType(DetailsActions.unitDetailsDestroyed))),
        map(_ => DetailsActions.activeUsersUpdatedOnBackend({unitId})),
      );
    }),
  ));

  constructor(private actions: Actions,
              private store: Store,
              private processUnitService: ProcessUnitService,
              private recentRunsService: RecentRunsService,
              private pubSubService: PubSubService) {}
}
