import { createAction, props } from '@ngrx/store';
import { Method, MethodLine } from '../../../api';

const source = '[Method Editor] ';

export class MethodEditorActions {
  static monacoEditorComponentInitialized = createAction(source + 'Monaco Editor Component Initialized');
  static methodEditorComponentInitializedForUnit = createAction(source + 'Method Editor Component Initialized For Unit',
    props<{ unitId: string }>());
  static methodEditorComponentInitializedForBatchJob = createAction(source + 'Method Editor Component Initialized For Batch Job',
    props<{ batchJobId: string }>());
  static modelSaved = createAction(source + 'Model Saved');
  static linesChanged = createAction(source + 'Lines Changed', props<{ lines: MethodLine[] }>());
  static saveButtonClicked = createAction(source + 'Save Button Clicked');
  static saveKeyboardShortcutPressed = createAction(source + 'Save Keyboard Shortcut Pressed');
  static methodFetched = createAction(source + 'Method Fetched', props<{ method: Method }>());
  static methodPolled = createAction(source + 'Method Polled', props<{ method: Method, unitId: string }>());
  static monacoEditorComponentDestroyed = createAction(source + 'Monaco Editor Component Destroyed');
  static methodEditorComponentDestroyed = createAction(source + 'Method Editor Component Destroyed');
}
