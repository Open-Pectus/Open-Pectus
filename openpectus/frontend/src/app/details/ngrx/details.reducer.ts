import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { CommandExample } from '../../api/models/CommandExample';
import { ControlState } from '../../api/models/ControlState';
import { ErrorLog } from '../../api/models/ErrorLog';
import { RecentRun } from '../../api/models/RecentRun';
import { DetailsActions } from './details.actions';

export interface DetailsState {
  allProcessValues: boolean;
  commandExamples: CommandExample[];
  controlState: ControlState;
  recentRun?: RecentRun;
  errorLog: ErrorLog;
}

const initialState: DetailsState = {
  allProcessValues: false,
  commandExamples: [],
  errorLog: {entries: []},
  controlState: {
    is_running: false,
    is_holding: false,
    is_paused: false,
  },
};

const reducer = createReducer(initialState,
  on(DetailsActions.unitDetailsInitialized, state => produce(state, draft => {
    draft.allProcessValues = false;
  })),
  on(DetailsActions.commandExamplesFetched, (state, {commandExamples}) => produce(state, draft => {
    draft.commandExamples = commandExamples;
  })),
  on(DetailsActions.controlStateFetched, (state, {controlState}) => produce(state, draft => {
    draft.controlState = controlState;
  })),
  on(DetailsActions.recentRunFetched, (state, {recentRun}) => produce(state, draft => {
    draft.recentRun = recentRun;
  })),
  on(DetailsActions.toggleAllProcessValues, (state, {allProcessValues}) => produce(state, draft => {
    draft.allProcessValues = allProcessValues;
  })),
);

export const detailsSlice = {name: 'details', reducer};
