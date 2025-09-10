import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { ActiveUser, AggregatedErrorLog, ApiError, CommandExample, ControlState, ProcessDiagram, ProcessValue, RecentRun } from '../../api';
import { DetailsActions } from './details.actions';
import { UnitControlCommands } from '../unit-control-commands.';

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
  otherActiveUsers: ActiveUser[];
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
  otherActiveUsers: [],
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
  on(DetailsActions.otherActiveUsersFetched, (state, {otherActiveUsers}) => produce(state, draft => {
    draft.otherActiveUsers = otherActiveUsers;
  })),
  on(DetailsActions.processUnitCommandButtonClicked, (state, {command}) => produce(state, draft => {
    if(command === UnitControlCommands.Start) draft.controlState.is_running = true;
    if(command === UnitControlCommands.Stop) draft.controlState.is_running = false;
    if(command === UnitControlCommands.Pause) draft.controlState.is_paused = true;
    if(command === UnitControlCommands.Unpause) draft.controlState.is_paused = false;
    if(command === UnitControlCommands.Hold) draft.controlState.is_holding = true;
    if(command === UnitControlCommands.Unhold) draft.controlState.is_holding = false;
  }))
);

export const detailsSlice = {name: 'details', reducer};
