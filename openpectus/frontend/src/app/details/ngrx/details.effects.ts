import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { debounceTime, map, mergeMap, of, skipWhile, switchMap } from 'rxjs';
import { CommandSource, ProcessUnitService } from '../../api';
import { selectRouteParam } from '../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../details-routing-url-parts';
import { DetailsActions } from './details.actions';
import { DetailsSelectors } from './details.selectors';

@Injectable()
export class DetailsEffects {
  saveMethodEditorModel = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.methodEditorModelSaveRequested),
    concatLatestFrom(() => this.store.select(DetailsSelectors.methodEditorContent)),
    switchMap(([_, content]) => {
      /* save model to backend */
      alert(`model saved! ${content}`);
      return of(DetailsActions.methodEditorModelSaved());
    }),
  ));

  fetchProcessValuesWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processValuesInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      if(isNaN(unitIdAsNumber)) return of(DetailsActions.processValuesFailedToLoad());
      return this.processUnitService.getProcessValues(unitIdAsNumber).pipe(
        map(processValues => DetailsActions.processValuesFetched({processValues})),
      );
    }),
  ));

  continuouslyPollProcessValues = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processValuesFetched),
    concatLatestFrom(() => [
      this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName)),
      this.store.select(DetailsSelectors.shouldPollProcessValues),
    ]),
    debounceTime(500),
    skipWhile(([_, __, shouldPoll]) => !shouldPoll),
    switchMap(([_, unitId, __]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      if(isNaN(unitIdAsNumber)) return of(DetailsActions.processValuesFailedToLoad());
      return this.processUnitService.getProcessValues(unitIdAsNumber).pipe(
        map(processValues => DetailsActions.processValuesFetched({processValues})),
      );
    }),
  ));

  executeProcessValueCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processValueCommandClicked),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([{command, processValueName}, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      return this.processUnitService.executeCommand(
        unitIdAsNumber, {...command, source: CommandSource.PROCESS_VALUE});
    }),
  ), {dispatch: false});

  executeUnitControlCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processUnitCommandButtonClicked),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    mergeMap(([{command}, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      return this.processUnitService.executeCommand(
        unitIdAsNumber, {...command});
    }),
  ), {dispatch: false});

  executeManuallyEnteredCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.commandsComponentExecuteClicked),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([{command}, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      return this.processUnitService.executeCommand(
        unitIdAsNumber, {...command});
    }),
  ), {dispatch: false});

  fetchProcessDiagramWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processDiagramInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      return this.processUnitService.getProcessDiagram(unitIdAsNumber).pipe(
        map(processDiagram => DetailsActions.processDiagramFetched({processDiagram})),
      );
    }),
  ));

  fetchCommandExamplesWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.commandsComponentInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      return this.processUnitService.getCommandExamples(unitIdAsNumber).pipe(
        map(commandExamples => DetailsActions.commandExamplesFetched({commandExamples})),
      );
    }),
  ));

  fetchRunLogWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.runLogComponentInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      return this.processUnitService.getRunLog(unitIdAsNumber).pipe(
        map(runLogLines => DetailsActions.runLogLinesFetched({runLogLines})),
      );
    }),
  ));

  constructor(private actions: Actions, private store: Store, private processUnitService: ProcessUnitService) {}
}
