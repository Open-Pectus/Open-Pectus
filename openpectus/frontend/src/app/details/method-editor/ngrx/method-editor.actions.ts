import { createAction, props } from '@ngrx/store';
import { Method } from '../../../api';

const source = '[Method Editor] ';

export class MethodEditorActions {
  static monacoEditorComponentInitialized = createAction(source + 'Monaco Editor Component Initialized');
  static methodEditorComponentInitialized = createAction(source + 'Method Editor Component Initialized');
  static modelSaved = createAction(source + 'Model Saved');
  static modelChanged = createAction(source + 'Model Changed', props<{ model: string }>());
  static modelSaveRequested = createAction(source + 'Model Save Requested');
  static methodFetched = createAction(source + 'Method Fetched', props<{ method: Method }>());
  static monacoEditorComponentDestroyed = createAction(source + 'Monaco Editor Component Destroyed');
}
