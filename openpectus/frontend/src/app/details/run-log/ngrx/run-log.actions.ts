import { createAction, props } from '@ngrx/store';
import { RunLog } from '../../../api';

const source = '[Run Log] ';

export class RunLogActions {
  static runLogComponentInitialized = createAction(source + 'Run Log Component Initialized');
  static runLogFetched = createAction(source + 'Run Log Fetched', props<{ runLog: RunLog }>());
  static runLogOnlyRunningFilterChanged = createAction(source + 'Run Log OnlyRunning Filter Changed', props<{ onlyRunning: boolean }>());
  static runLogFilterTextChanged = createAction(source + 'Run Log Filter Text Changed', props<{ filterText: string }>());
}
