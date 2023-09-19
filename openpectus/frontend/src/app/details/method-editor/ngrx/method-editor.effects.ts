import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { map, of, switchMap } from 'rxjs';
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
      this.store.select(MethodEditorSelectors.methodEditorContent),
    ]),
    switchMap(([_, unitId, content]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.saveMethod(unitId, {content: content ?? ''}).pipe(map(() => MethodEditorActions.modelSaved()));
    }),
  ));

  fetchContentWhenComponentInitialized = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorComponentInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, id]) => {
      if(id === undefined) return of();
      return this.processUnitService.getMethod(id).pipe(map(method => MethodEditorActions.methodFetched({method})));
    }),
  ));

  constructor(private actions: Actions, private store: Store, private processUnitService: ProcessUnitService) {}
}
