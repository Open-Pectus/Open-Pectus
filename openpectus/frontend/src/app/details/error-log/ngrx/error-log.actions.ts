import { createAction, props } from '@ngrx/store';
import { ErrorLog } from '../../../api';

const source = '[Error Log] ';

export class ErrorLogActions {
  static errorLogComponentInitializedForUnit = createAction(source + 'Error Log Component Initialized For Unit', props<{ unitId: string }>());
  static errorLogComponentInitializedForRecentRun = createAction(source + 'Error Log Component Initialized For Recent Run',
    props<{ recentRunId: string }>());
  static errorLogComponentDestroyed = createAction(source + 'Error Log Component Destroyed');
  static errorLogFetched = createAction(source + 'Error Log Fetched', props<{ errorLog: ErrorLog }>());
  static errorLogUpdatedOnBackend = createAction(source + 'Error Log Updated On Backend', props<{ unitId: string }>());
}
