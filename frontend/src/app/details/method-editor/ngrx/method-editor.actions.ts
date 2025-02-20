import { createAction, props } from '@ngrx/store';
import { MethodAndState, MethodLine } from '../../../api';

const source = '[Method Editor] ';

export class MethodEditorActions {
  static methodEditorComponentInitializedForUnit = createAction(source + 'Method Editor Component Initialized For Unit',
    props<{ unitId: string }>());
  static methodEditorComponentInitializedForRecentRun = createAction(source + 'Method Editor Component Initialized For Recent Run',
    props<{ recentRunId: string }>());
  static methodEditorComponentDestroyed = createAction(source + 'Method Editor Component Destroyed');
  static monacoEditorComponentInitialized = createAction(source + 'Monaco Editor Component Initialized');
  static monacoEditorComponentDestroyed = createAction(source + 'Monaco Editor Component Destroyed');
  static methodFetchedInitially = createAction(source + 'Method Fetched Initially', props<{ methodAndState: MethodAndState }>());
  static methodFetchedDueToUpdate = createAction(source + 'Method Fetched Due To Update', props<{ methodAndState: MethodAndState }>());
  static linesChanged = createAction(source + 'Lines Changed', props<{ lines: MethodLine[] }>());
  static saveButtonClicked = createAction(source + 'Save Button Clicked');
  static saveKeyboardShortcutPressed = createAction(source + 'Save Keyboard Shortcut Pressed');
  static modelSaved = createAction(source + 'Model Saved');
  static methodUpdatedOnBackend = createAction(source + 'Method Updated On Backend', props<{ unitId: string }>());
}
