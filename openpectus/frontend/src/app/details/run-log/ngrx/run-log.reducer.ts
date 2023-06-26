import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { RunLog } from '../../../api';
import { RunLogActions } from './run-log.actions';

export interface RunLogState {
  runLog: RunLog;
  onlyRunning: boolean;
  filterText: string;
  dateFormat: string;
}

const initialState: RunLogState = {
  runLog: {lines: []},
  onlyRunning: false,
  filterText: '',
  dateFormat: 'MM-dd HH:mm:ss',
};

const reducer = createReducer(initialState,
  on(RunLogActions.runLogFetched, (state, {runLog}) => produce(state, draft => {
    draft.runLog = runLog;
  })),
  on(RunLogActions.runLogOnlyRunningFilterChanged, (state, {onlyRunning}) => produce(state, draft => {
    draft.onlyRunning = onlyRunning;
  })),
  on(RunLogActions.runLogFilterTextChanged, (state, {filterText}) => produce(state, draft => {
    draft.filterText = filterText;
  })),
);

export const runLogSlice = {name: 'runLog', reducer};
