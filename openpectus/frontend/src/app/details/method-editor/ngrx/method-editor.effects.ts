import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { debounceTime, map, of, switchMap } from 'rxjs';
import { ProcessUnitService } from '../../../api';
import { selectRouteParam } from '../../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../../details-routing-url-parts';
import { MethodEditorActions } from './method-editor.actions';
import { MethodEditorSelectors } from './method-editor.selectors';

@Injectable()
export class MethodEditorEffects {
  saveMethodEditorModel = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.modelSaveRequested),
    concatLatestFrom(() => [
      this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName)),
      this.store.select(MethodEditorSelectors.content),
    ]),
    switchMap(([_, unitId, content]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.saveMethod(unitId, {content: content ?? '', locked_lines: [], injected_lines: []}).pipe(
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

  continuouslyPollMethod = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodFetched),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    debounceTime(5000), // delay() in MSW doesn't work in Firefox, so to avoid freezing the application in FF, we debounce
    switchMap(([_, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getMethod(unitId).pipe(map(method => MethodEditorActions.methodFetched({method})));
    }),
  ));

  constructor(private actions: Actions, private store: Store, private processUnitService: ProcessUnitService) {}
}
