import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { catchError, delay, filter, map, mergeMap, of, switchMap, takeUntil } from 'rxjs';
import { CommandSource, ProcessUnitService, RecentRunsService } from '../../api';
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
      return this.processUnitService.getProcessValues(unitId).pipe(
        map(processValues => DetailsActions.processValuesFetched({processValues})),
        catchError(() => of(DetailsActions.processValuesFailedToLoad())),
      );
    }),
  ));

  // TODO: When we introduce websocket pubsub, figure out if it makes sense to push process_value changes through it, or polling is fine.
  continuouslyPollProcessValues = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processValuesFetched, DetailsActions.processValuesFailedToLoad),
    delay(1000),
    concatLatestFrom(() => [
      this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName)),
      this.store.select(DetailsSelectors.shouldPoll),
    ]),
    filter(([_, __, shouldPoll]) => shouldPoll),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getProcessValues(unitId).pipe(
        map(processValues => DetailsActions.processValuesFetched({processValues})),
        catchError(() => of(DetailsActions.processValuesFailedToLoad())),
      );
    }),
  ));

  fetchControlStateWhenPageInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.unitDetailsInitialized),
    switchMap(({unitId}) => {
      return this.processUnitService.getControlState(unitId).pipe(
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

  subscribeForErrorLogUpdatesFromBackend = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.unitDetailsInitialized),
    mergeMap(({unitId}) => {
      return this.pubSubService.subscribeErrorLog(unitId).pipe(
        takeUntil(this.actions.pipe(ofType(DetailsActions.unitDetailsDestroyed))),
        map(_ => DetailsActions.errorLogUpdatedOnBackend({unitId})),
      );
    }),
  ));

  fetchControlStateOnUpdateFromBackend = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.controlStateUpdatedOnBackend),
    mergeMap(({unitId}) => {
      return this.processUnitService.getControlState(unitId).pipe(
        map(controlState => DetailsActions.controlStateFetched({controlState})),
      );
    }),
  ));

  fetchErrorLogOnUpdateFromBackend = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.errorLogUpdatedOnBackend),
    mergeMap(({unitId}) => {
      return this.processUnitService.getErrorLog(unitId).pipe(
        map(errorLog => DetailsActions.errorLogFetched({errorLog})),
      );
    }),
  ));

  executeUnitControlCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processUnitCommandButtonClicked),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    mergeMap(([{command}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.executeCommand(unitId, {command, source: CommandSource.UNIT_BUTTON});
    }),
  ), {dispatch: false});

  executeManuallyEnteredCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.commandsComponentExecuteClicked),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([{command}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.executeCommand(unitId, {...command});
    }),
  ), {dispatch: false});

  fetchProcessDiagramWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processDiagramInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getProcessDiagram(unitId).pipe(
        map(processDiagram => DetailsActions.processDiagramFetched({processDiagram})),
      );
    }),
  ));

  fetchCommandExamplesWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.commandsComponentInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getCommandExamples(unitId).pipe(
        map(commandExamples => DetailsActions.commandExamplesFetched({commandExamples})),
      );
    }),
  ));

  fetchRecentRunWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.recentRunDetailsInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.recentRunIdParamName))),
    switchMap(([_, recentRunId]) => {
      if(recentRunId === undefined) return of();
      return this.recentRunsService.getRecentRun(recentRunId).pipe(
        map(recentRun => DetailsActions.recentRunFetched({recentRun})),
      );
    }),
  ));

  downloadRecentRunCsvWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.recentRunDownloadCsvButtonClicked),
    switchMap(({recentRunId}) => {
      return this.recentRunsService.getRecentRunCsvJson(recentRunId).pipe(
        map(RecentRunCsv => {
          const link = document.createElement('a');
          link.download = RecentRunCsv.filename;
          link.href = URL.createObjectURL(new Blob([RecentRunCsv.csv_content]));
          link.click();
        }),
      );
    }),
  ), {dispatch: false});

  constructor(private actions: Actions,
              private store: Store,
              private processUnitService: ProcessUnitService,
              private recentRunsService: RecentRunsService,
              private pubSubService: PubSubService) {}
}
