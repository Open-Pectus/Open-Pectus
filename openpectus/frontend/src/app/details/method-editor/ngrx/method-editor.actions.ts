import { createAction, props } from '@ngrx/store';

const source = '[Method Editor] ';

export class MethodEditorActions {
  static methodEditorInitialized = createAction(source + 'Method Editor Initialized');
  static methodEditorModelSaved = createAction(source + 'Method Editor Model Saved');
  static methodEditorModelChanged = createAction(source + 'Method Editor Model Changed', props<{ model: string }>());
  static methodEditorModelSaveRequested = createAction(source + 'Method Editor Model Save Requested');
}
