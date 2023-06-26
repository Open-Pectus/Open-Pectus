import { createAction, props } from '@ngrx/store';

const source = '[Method Editor] ';

export class MethodEditorActions {
  static monacoEditorComponentInitialized = createAction(source + 'Monaco Editor Component Initialized');
  static modelSaved = createAction(source + 'Model Saved');
  static modelChanged = createAction(source + 'Model Changed', props<{ model: string }>());
  static modelSaveRequested = createAction(source + 'Model Save Requested');
}
