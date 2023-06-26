import { createAction, props } from '@ngrx/store';
import { RunLog } from '../../../api';

const source = '[Run Log] ';

export class RunLogActions {
  static runLogComponentInitialized = createAction(source + 'Run Log Component Initialized');
  static runLogFetched = createAction(source + 'Run Log Fetched', props<{ runLog: RunLog }>());
}
