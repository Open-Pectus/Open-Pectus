import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { debounceTime, filter, map, mergeMap, of, switchMap } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ProcessUnitService } from '../../api';
import { selectRouteParam } from '../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../details-routing-url-parts';
import { DetailsActions } from './details.actions';
import { DetailsSelectors } from './details.selectors';

@Injectable()
export class DetailsEffects {
  fetchProcessValuesWhenPageInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.unitDetailsInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of(DetailsActions.processValuesFailedToLoad());
      return this.processUnitService.getProcessValues(unitId).pipe(
        map(processValues => DetailsActions.processValuesFetched({processValues})),
        catchError(() => of(DetailsActions.processValuesFailedToLoad())),
      );
    }),
  ));

  continuouslyPollProcessValues = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processValuesFetched, DetailsActions.processValuesFailedToLoad),
    concatLatestFrom(() => [
      this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName)),
      this.store.select(DetailsSelectors.shouldPollProcessValues),
    ]),
    debounceTime(1000), // delay() in MSW doesn't work in Firefox, so to avoid freezing the application in FF, we debounce
    filter(([_, __, shouldPoll]) => shouldPoll),
    switchMap(([_, unitId, __]) => {
      if(unitId === undefined) return of(DetailsActions.processValuesFailedToLoad());
      return this.processUnitService.getProcessValues(unitId).pipe(
        map(processValues => DetailsActions.processValuesFetched({processValues})),
        catchError(() => of(DetailsActions.processValuesFailedToLoad())),
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
