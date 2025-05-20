import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { ActiveUser, AggregatedErrorLog, ApiError, CommandExample, ControlState, ProcessDiagram, ProcessValue, RecentRun } from '../../api';
import { DetailsActions } from './details.actions';

export interface DetailsState {
  processValues: ProcessValue[];
  allProcessValues: boolean;
  processDiagram?: ProcessDiagram;
  commandExamples: CommandExample[];
  controlState: ControlState;
  recentRun?: RecentRun;
  shouldPoll: boolean;
  errorLog: AggregatedErrorLog;
  missingRoles?: string[];
  activeUsers: ActiveUser[];
}

const initialState: DetailsState = {
  processValues: [],
  allProcessValues: false,
  commandExamples: [],
  shouldPoll: false,
  errorLog: {entries: []},
  controlState: {
    is_running: false,
    is_holding: false,
    is_paused: false,
  },
  activeUsers: [],
};

export interface MissingRoleApiError extends ApiError {
  body: { detail: { missing_roles?: string[] } };
}

const isMissingRoleError = (error: ApiError): error is MissingRoleApiError => {
  return error.status === 403
         && typeof error.body === 'object'
         && Array.isArray((error as MissingRoleApiError).body?.detail?.missing_roles);
};

const reducer = createReducer(initialState,
  on(DetailsActions.unitDetailsInitialized, state => produce(state, draft => {
    draft.shouldPoll = true;
    draft.allProcessValues = false;
  })),
  on(DetailsActions.unitDetailsDestroyed, state => produce(state, draft => {
    draft.shouldPoll = false;
  })),
  on(DetailsActions.processValuesFetched, (state, {processValues}) => produce(state, draft => {
    draft.processValues = processValues;
    draft.missingRoles = undefined;
  })),
  on(DetailsActions.processValuesFailedToLoad, (state, {error}) => produce(state, draft => {
    if(isMissingRoleError(error)) draft.missingRoles = error.body.detail.missing_roles;
  })),
  on(DetailsActions.processDiagramFetched, (state, {processDiagram}) => produce(state, draft => {
    draft.processDiagram = processDiagram;
  })),
  on(DetailsActions.commandExamplesFetched, (state, {commandExamples}) => produce(state, draft => {
    draft.commandExamples = commandExamples;
  })),
  on(DetailsActions.controlStateFetched, (state, {controlState}) => produce(state, draft => {
    draft.controlState = controlState;
  })),
  on(DetailsActions.recentRunFetched, (state, {recentRun}) => produce(state, draft => {
    draft.recentRun = recentRun;
    draft.missingRoles = undefined;
  })),
  on(DetailsActions.recentRunFailedToLoad, (state, {error}) => produce(state, draft => {
    if(isMissingRoleError(error)) draft.missingRoles = error.body.detail.missing_roles;
  })),
  on(DetailsActions.toggleAllProcessValues, (state, {allProcessValues}) => produce(state, draft => {
    draft.allProcessValues = allProcessValues;
  })),
  on(DetailsActions.activeUsersFetched, (state, {activeUsers}) => produce(state, draft => {
    draft.activeUsers = activeUsers;
  })),
);

export const detailsSlice = {name: 'details', reducer};
