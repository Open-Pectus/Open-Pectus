import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { map, mergeMap, of, switchMap, takeUntil } from 'rxjs';
import { BatchJobService, ProcessUnitService } from '../../../api';
import { selectRouteParam } from '../../../ngrx/router.selectors';
import { PubSubService } from '../../../shared/pub-sub.service';
import { DetailsRoutingUrlParts } from '../../details-routing-url-parts';
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
      return this.processUnitService.getMethod(unitId).pipe(map(method => MethodEditorActions.methodFetchedInitially({method})));
    }),
  ));

  fetchContentWhenComponentInitializedForBatchJob = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorComponentInitializedForBatchJob),
    switchMap(({batchJobId}) => {
      if(batchJobId === undefined) return of();
      return this.batchJobService.getBatchJobMethod(batchJobId).pipe(map(method => MethodEditorActions.methodFetchedInitially({method})));
    }),
  ));

  subscribeForUpdatesFromBackend = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorComponentInitializedForUnit),
    mergeMap(({unitId}) => {
      return this.pubSubService.subscribeRunLog(unitId).pipe(
        takeUntil(this.actions.pipe(ofType(MethodEditorActions.methodEditorComponentDestroyed))),
        map(_ => MethodEditorActions.methodUpdatedOnBackend({unitId})),
      );
    }),
  ));

  fetchOnUpdateFromBackend = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodUpdatedOnBackend),
    mergeMap(({unitId}) => {
      return this.processUnitService.getMethod(unitId).pipe(
        map(method => MethodEditorActions.methodFetchedDueToUpdate({method})),
      );
    }),
  ));

  constructor(private actions: Actions, private store: Store,
              private processUnitService: ProcessUnitService,
              private batchJobService: BatchJobService,
              private pubSubService: PubSubService) {}
}
