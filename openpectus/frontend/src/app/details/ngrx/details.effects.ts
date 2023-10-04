import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { catchError, debounceTime, delayWhen, map, mergeMap, of, switchMap, takeUntil, timer } from 'rxjs';
import { ProcessUnitService } from '../../api';
import { selectRouteParam } from '../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../details-routing-url-parts';
import { DetailsActions } from './details.actions';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class DetailsEffects {
  fetchProcessValuesWhenPageInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.unitDetailsInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getProcessValues(unitId).pipe(
        map(processValues => DetailsActions.processValuesFetched({processValues})),
        catchError(() => of(DetailsActions.processValuesFailedToLoad())),
      );
    }),
  ));

  // TODO: When we introduce websocket pubsub, figure out if it makes sense to push process_value changes through it, or polling is fine.
  continuouslyPollProcessValues = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processValuesFetched, DetailsActions.processValuesFailedToLoad),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    debounceTime(1000),
    takeUntil(this.actions.pipe(ofType(DetailsActions.unitDetailsDestroyed))),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getProcessValues(unitId).pipe(
        map(processValues => DetailsActions.processValuesFetched({processValues})),
        catchError(() => of(DetailsActions.processValuesFailedToLoad())),
      );
    }),
  ));

  // TODO: this should be gotten via push through websocket instead of polling.
  continuouslyPollControlState = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.unitDetailsInitialized, DetailsActions.controlStateFetched),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    delayWhen(([action, _]) => {
      return action.type === DetailsActions.unitDetailsInitialized.type ? of(0) : timer(500);
    }),
    takeUntil(this.actions.pipe(ofType(DetailsActions.unitDetailsDestroyed))),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getControlState(unitId).pipe(
        map(controlState => DetailsActions.controlStateFetched({controlState})),
      );
    }),
  ));

  executeUnitControlCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processUnitCommandButtonClicked),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    mergeMap(([{command}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.executeCommand(unitId, {...command});
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

  constructor(private actions: Actions, private store: Store, private processUnitService: ProcessUnitService) {}
}
