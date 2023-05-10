import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { map, of, switchMap } from 'rxjs';
import { CommandSource, DefaultService } from '../../api';
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

  loadProcessValuesWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processValuesInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      if(isNaN(unitIdAsNumber)) return of(DetailsActions.processValuesFailedToLoad());
      return this.apiService.getProcessValuesProcessUnitIdProcessValuesGet(unitIdAsNumber).pipe(
        map(processValues => DetailsActions.processValuesLoaded({processValues})),
      );
    }),
  ));

  executeProcessValueCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processValueCommandClicked),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([{command, processValueName}, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      return this.apiService.executeCommandProcessUnitUnitIdExecuteCommandPost(
        unitIdAsNumber, {...command, source: CommandSource.PROCESS_VALUE});
    }),
  ), {dispatch: false});

  executeUnitControlCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processUnitCommandButtonClicked),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    map(([{command}, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      this.apiService.executeCommandProcessUnitUnitIdExecuteCommandPost(
        unitIdAsNumber, {...command});
    }),
  ), {dispatch: false});

  loadProcessDiagramWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processDiagramInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      const unitIdAsNumber = parseInt(unitId ?? '');
      return this.apiService.getProcessDiagramProcessUnitUnitIdProcessDiagramGet(unitIdAsNumber).pipe(
        map(processDiagram => DetailsActions.processDiagramFetched({processDiagram})),
      );
    }),
  ));

  constructor(private actions: Actions, private store: Store, private apiService: DefaultService) {}
}
