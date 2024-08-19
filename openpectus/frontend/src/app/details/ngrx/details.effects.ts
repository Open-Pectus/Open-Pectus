import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { map, mergeMap, of, switchMap, takeUntil } from 'rxjs';
import { CommandSource } from '../../api/models/CommandSource';
import { ProcessUnitService } from '../../api/services/ProcessUnitService';
import { RecentRunsService } from '../../api/services/RecentRunsService';
import { selectRouteParam } from '../../ngrx/router.selectors';
import { PubSubService } from '../../shared/pub-sub.service';
import { DetailsRoutingUrlParts } from '../details-routing-url-parts';
import { DetailsActions } from './details.actions';
import { DetailsSelectors } from './details.selectors';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class DetailsEffects {
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


  fetchControlStateOnUpdateFromBackend = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.controlStateUpdatedOnBackend),
    mergeMap(({unitId}) => {
      return this.processUnitService.getControlState(unitId).pipe(
        map(controlState => DetailsActions.controlStateFetched({controlState})),
      );
    }),
  ));

  executeUnitControlCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processUnitCommandButtonClicked),
    concatLatestFrom(() => this.store.select(DetailsSelectors.processUnitId)),
    mergeMap(([{command}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.executeCommand(unitId, {command, source: CommandSource.UNIT_BUTTON});
    }),
  ), {dispatch: false});

  executeManuallyEnteredCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.commandsComponentExecuteClicked),
    concatLatestFrom(() => this.store.select(DetailsSelectors.processUnitId)),
    switchMap(([{command}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.executeCommand(unitId, {...command});
    }),
  ), {dispatch: false});

  fetchCommandExamplesWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.commandsComponentInitialized),
    concatLatestFrom(() => this.store.select(DetailsSelectors.processUnitId)),
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
