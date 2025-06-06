import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { map, mergeMap, of, switchMap, takeUntil } from 'rxjs';
import { ProcessUnitService, RecentRunsService } from '../../../api';
import { PubSubService } from '../../../shared/pub-sub.service';
import { DetailsSelectors } from '../../ngrx/details.selectors';
import { MethodEditorActions } from './method-editor.actions';
import { MethodEditorSelectors } from './method-editor.selectors';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class MethodEditorEffects {
  saveMethodEditorModel = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.saveButtonClicked, MethodEditorActions.saveKeyboardShortcutPressed),
    concatLatestFrom(() => [
      this.store.select(DetailsSelectors.processUnitId),
      this.store.select(MethodEditorSelectors.method),
    ]),
    switchMap(([_, unitId, method]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.saveMethod({unitId, requestBody: method}).pipe(
        map(response => MethodEditorActions.modelSaved({newVersion: response.version})));
    }),
  ));

  fetchContentWhenComponentInitializedForUnit = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorComponentInitializedForUnit),
    switchMap(({unitId}) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getMethodAndState({unitId}).pipe(
        map(methodAndState => MethodEditorActions.methodFetchedInitially({methodAndState})));
    }),
  ));

  fetchContentWhenComponentInitializedForRecentRun = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorComponentInitializedForRecentRun),
    switchMap(({recentRunId}) => {
      if(recentRunId === undefined) return of();
      return this.recentRunsService.getRecentRunMethodAndState({runId: recentRunId}).pipe(
        map(methodAndState => MethodEditorActions.methodFetchedInitially({methodAndState})));
    }),
  ));

  subscribeForMethodUpdatesFromBackend = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorComponentInitializedForUnit),
    mergeMap(({unitId}) => {
      return this.pubSubService.subscribeMethod(unitId).pipe(
        takeUntil(this.actions.pipe(ofType(MethodEditorActions.methodEditorComponentDestroyed))),
        map(_ => MethodEditorActions.methodUpdatedOnBackend({unitId})),
      );
    }),
  ));

  subscribeForMethodStateUpdatesFromBackend = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorComponentInitializedForUnit),
    mergeMap(({unitId}) => {
      return this.pubSubService.subscribeMethodState(unitId).pipe(
        takeUntil(this.actions.pipe(ofType(MethodEditorActions.methodEditorComponentDestroyed))),
        map(_ => MethodEditorActions.methodStateUpdatedOnBackend({unitId})),
      );
    }),
  ));

  fetchMethodOnUpdateFromBackend = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodUpdatedOnBackend),
    mergeMap(({unitId}) => {
      return this.processUnitService.getMethod({unitId}).pipe(
        map(method => MethodEditorActions.methodFetchedDueToUpdate({method})),
      );
    }),
  ));

  fetchMethodStateOnUpdateFromBackend = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodStateUpdatedOnBackend),
    mergeMap(({unitId}) => {
      return this.processUnitService.getMethodAndState({unitId}).pipe(
        map(methodAndState => MethodEditorActions.methodStateFetchedDueToUpdate({methodAndState})),
      );
    }),
  ));

  fetchMethodRefreshRequest = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodRefreshRequested),
    mergeMap(({unitId}) => {
      return this.processUnitService.getMethod({unitId}).pipe(
        map(method => MethodEditorActions.methodFetchedDueToUpdate({method})),
      );
    }),
  ));

  constructor(private actions: Actions, private store: Store,
              private processUnitService: ProcessUnitService,
              private recentRunsService: RecentRunsService,
              private pubSubService: PubSubService) {}
}
