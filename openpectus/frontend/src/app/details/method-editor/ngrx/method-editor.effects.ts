import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { debounceTime, map, of, switchMap } from 'rxjs';
import { ProcessUnitService } from '../../../api';
import { selectRouteParam } from '../../../ngrx/router.selectors';
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

  fetchContentWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorComponentInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getMethod(unitId).pipe(map(method => MethodEditorActions.methodFetched({method})));
    }),
  ));

  // TODO: Should be websocket in future, not polling.
  continuouslyPollMethod = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodFetched, MethodEditorActions.methodPolled),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    debounceTime(10000), // delay() in MSW doesn't work in Firefox, so to avoid freezing the application in FF, we debounce
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getMethod(unitId).pipe(map(method => MethodEditorActions.methodPolled({method})));
    }),
  ));

  constructor(private actions: Actions, private store: Store, private processUnitService: ProcessUnitService) {}
}
