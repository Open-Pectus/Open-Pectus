import { createAction, props } from '@ngrx/store';
import { Method, MethodAndState, MethodLine } from '../../../api';

const source = '[Method Editor] ';

export class MethodEditorActions {
  static methodEditorComponentInitializedForUnit = createAction(source + 'Method Editor Component Initialized For Unit',
    props<{ unitId: string }>());
  static methodEditorComponentInitializedForRecentRun = createAction(source + 'Method Editor Component Initialized For Recent Run',
    props<{ recentRunId: string }>());
  static methodEditorComponentDestroyed = createAction(source + 'Method Editor Component Destroyed');
  static methodFetchedInitially = createAction(source + 'Method Fetched Initially', props<{ methodAndState: MethodAndState }>());
  static methodFetchedDueToUpdate = createAction(source + 'Method Fetched Due To Update', props<{ method: Method }>());
  static methodStateFetchedDueToUpdate = createAction(source + 'Method State Fetched Due To Update',
    props<{ methodAndState: MethodAndState }>());
  static linesChanged = createAction(source + 'Lines Changed', props<{ lines: MethodLine[] }>());
  static saveButtonClicked = createAction(source + 'Save Button Clicked');
  static saveKeyboardShortcutPressed = createAction(source + 'Save Keyboard Shortcut Pressed');
  static modelSaved = createAction(source + 'Model Saved', props<{ newVersion: number }>());
  static methodUpdatedOnBackend = createAction(source + 'Method Updated On Backend', props<{ unitId: string }>());
  static methodStateUpdatedOnBackend = createAction(source + 'Method State Updated On Backend', props<{ unitId: string }>());
}
