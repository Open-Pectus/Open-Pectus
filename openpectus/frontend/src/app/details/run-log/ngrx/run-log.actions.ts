import { createAction, props } from '@ngrx/store';
import { RunLog } from '../../../api';

const source = '[Run Log] ';

export class RunLogActions {
  static runLogComponentInitializedForUnit = createAction(source + 'Run Log Component Initialized For Unit', props<{ unitId: string }>());
  static runLogComponentInitializedForBatchJob = createAction(source + 'Run Log Component Initialized For Batch Job',
    props<{ batchJobId: string }>());
  static runLogComponentDestroyed = createAction(source + 'Run Log Component Destroyed');
  static runLogFetched = createAction(source + 'Run Log Fetched', props<{ runLog: RunLog }>());
  static runLogPolledForUnit = createAction(source + 'Run Log Polled For Unit', props<{ runLog: RunLog, unitId: string }>());
  static onlyRunningFilterChanged = createAction(source + 'OnlyRunning Filter Changed', props<{ onlyRunning: boolean }>());
  static filterTextChanged = createAction(source + 'Filter Text Changed', props<{ filterText: string }>());
  static expandLine = createAction(source + 'Expand Line', props<{ id: number }>());
  static collapseLine = createAction(source + 'Collapse Line', props<{ id: number }>());
  static expandAll = createAction(source + 'Expand All');
  static collapseAll = createAction(source + 'Collapse All');
  static forceLineButtonClicked = createAction(source + 'Force Line Button Clicked', props<{ lineId: number }>());
  static cancelLineButtonClicked = createAction(source + 'Cancel Line Button Clicked', props<{ lineId: number }>());
}
