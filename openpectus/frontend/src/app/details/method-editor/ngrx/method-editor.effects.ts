import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { debounceTime, filter, map, of, switchMap } from 'rxjs';
import { BatchJobService, ProcessUnitService } from '../../../api';
import { selectRouteParam } from '../../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../../details-routing-url-parts';
import { DetailsSelectors } from '../../ngrx/details.selectors';
import { MethodEditorActions } from './method-editor.actions';
import { MethodEditorSelectors } from './method-editor.selectors';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class MethodEditorEffects {
  saveMethodEditorModel = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.saveButtonClicked, MethodEditorActions.saveKeyboardShortcutPressed),
    concatLatestFrom(() => [
      this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName)),
      this.store.select(MethodEditorSelectors.method),
    ]),
    switchMap(([_, unitId, method]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.saveMethod(unitId, method).pipe(
        map(() => MethodEditorActions.modelSaved()));
    }),
  ));

  fetchContentWhenComponentInitializedForUnit = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorComponentInitializedForUnit),
    switchMap(({unitId}) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getMethod(unitId).pipe(map(method => MethodEditorActions.methodFetched({method})));
    }),
  ));

  fetchContentWhenComponentInitializedForBatchJob = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorComponentInitializedForBatchJob),
    switchMap(({batchJobId}) => {
      if(batchJobId === undefined) return of();
      return this.batchJobService.getBatchJobMethod(batchJobId).pipe(map(method => MethodEditorActions.methodFetched({method})));
    }),
  ));

  // TODO: Should be websocket in future, not polling.
  continuouslyPollMethod = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorComponentInitializedForUnit, MethodEditorActions.methodPolledForUnit),
    debounceTime(10000),
    concatLatestFrom(() => this.store.select(DetailsSelectors.shouldPoll)),
    filter(([_, shouldPoll]) => shouldPoll),
    switchMap(([{unitId}]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getMethod(unitId).pipe(map(method => MethodEditorActions.methodPolledForUnit({method, unitId})));
    }),
  ));

  constructor(private actions: Actions, private store: Store,
              private processUnitService: ProcessUnitService,
              private batchJobService: BatchJobService) {}
}
