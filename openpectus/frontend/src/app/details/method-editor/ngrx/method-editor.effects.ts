import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { of, switchMap } from 'rxjs';
import { MethodEditorActions } from './method-editor.actions';
import { MethodEditorSelectors } from './method-editor.selectors';

@Injectable()
export class MethodEditorEffects {
  saveMethodEditorModel = createEffect(() => this.actions.pipe(
    ofType(MethodEditorActions.methodEditorModelSaveRequested),
    concatLatestFrom(() => this.store.select(MethodEditorSelectors.methodEditorContent)),
    switchMap(([_, content]) => {
      /* save model to backend */
      alert(`model saved! ${content}`);
      return of(MethodEditorActions.methodEditorModelSaved());
    }),
  ));

  constructor(private actions: Actions, private store: Store) {}
}
