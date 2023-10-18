import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { RunLog } from '../../../api';
import { RunLogActions } from './run-log.actions';

export interface RunLogState {
  runLog: RunLog;
  onlyRunning: boolean;
  filterText: string;
  expandedLines: number[];
}

const initialState: RunLogState = {
  runLog: {lines: []},
  onlyRunning: false,
  filterText: '',
  expandedLines: [],
};

const reducer = createReducer(initialState,
  on(RunLogActions.runLogComponentDestroyed, () => initialState),
  on(RunLogActions.runLogComponentInitializedForUnit, state => produce(state, draft => {
    draft.filterText = '';
    draft.onlyRunning = false;
  })),
  on(RunLogActions.runLogFetched, RunLogActions.runLogPolledForUnit, (state, {runLog}) => produce(state, draft => {
    draft.runLog = runLog;
  })),
  on(RunLogActions.onlyRunningFilterChanged, (state, {onlyRunning}) => produce(state, draft => {
    draft.onlyRunning = onlyRunning;
  })),
  on(RunLogActions.filterTextChanged, (state, {filterText}) => produce(state, draft => {
    draft.filterText = filterText;
  })),
  on(RunLogActions.expandLine, (state, {id}) => produce(state, draft => {
    draft.expandedLines.push(id);
  })),
  on(RunLogActions.collapseLine, (state, {id}) => produce(state, draft => {
    draft.expandedLines = draft.expandedLines.filter(expandedLineId => expandedLineId !== id);
  })),
  on(RunLogActions.expandAll, state => produce(state, draft => {
    draft.expandedLines = state.runLog.lines.map(line => line.id);
  })),
  on(RunLogActions.collapseAll, state => produce(state, draft => {
    draft.expandedLines = [];
  })),
);

export const runLogSlice = {name: 'runLog', reducer};
