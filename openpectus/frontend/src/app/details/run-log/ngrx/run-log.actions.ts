import { createAction, props } from '@ngrx/store';
import { RunLog } from '../../../api';

const source = '[Run Log] ';

export class RunLogActions {
  static runLogComponentInitialized = createAction(source + 'Run Log Component Initialized');
  static runLogFetched = createAction(source + 'Run Log Fetched', props<{ runLog: RunLog }>());
  static onlyRunningFilterChanged = createAction(source + 'Run Log OnlyRunning Filter Changed', props<{ onlyRunning: boolean }>());
  static filterTextChanged = createAction(source + 'Run Log Filter Text Changed', props<{ filterText: string }>());
  static expandLine = createAction(source + 'Expand Line', props<{ id: number }>());
  static collapseLine = createAction(source + 'Collapse Line', props<{ id: number }>());
  static expandAll = createAction(source + 'Expand All');
  static collapseAll = createAction(source + 'Collapse All');
}
