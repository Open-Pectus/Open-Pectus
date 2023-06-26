import { createAction, props } from '@ngrx/store';

export class MethodEditorActions {
  static prefix = '[Method Editor] ';
  static methodEditorInitialized = createAction(this.prefix + 'Method Editor Initialized');
  static methodEditorModelSaved = createAction(this.prefix + 'Method Editor Model Saved');
  static methodEditorModelChanged = createAction(this.prefix + 'Method Editor Model Changed', props<{ model: string }>());
  static methodEditorModelSaveRequested = createAction(this.prefix + 'Method Editor Model Save Requested');
}
