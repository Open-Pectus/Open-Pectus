import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { RunLog } from '../../../api';
import { RunLogActions } from './run-log.actions';

export interface RunLogState {
  runLog: RunLog;
}

const initialState: RunLogState = {
  runLog: {lines: []},
};

const reducer = createReducer(initialState,
  on(RunLogActions.runLogFetched, (state, {runLog}) => produce(state, draft => {
    draft.runLog = runLog;
  })),
);

export const runLogSlice = {name: 'runLog', reducer};
