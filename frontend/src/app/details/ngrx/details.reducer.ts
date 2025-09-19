import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { ActiveUser, AggregatedErrorLog, ApiError, CommandExample, ControlState, ProcessDiagram, ProcessValue, RecentRun } from '../../api';
import { DetailsActions } from './details.actions';
import { UnitControlCommands } from '../unit-control-commands.';

export interface OptimisticClickedControlButtons {
  start: boolean,
  hold: boolean,
  pause: boolean,
  stop: boolean,
}

export interface DetailsState {
  processValues: ProcessValue[];
  allProcessValues: boolean;
  processDiagram?: ProcessDiagram;
  commandExamples: CommandExample[];
  controlState: ControlState;
  optimisticClickedControlButtons: OptimisticClickedControlButtons;
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
  optimisticClickedControlButtons: {
    start: false,
    hold: false,
    pause: false,
    stop: false,
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
    draft.optimisticClickedControlButtons = {start: false, stop: false, pause: false, hold: false};
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
    if(command === UnitControlCommands.Start) draft.optimisticClickedControlButtons.start = true;
    if(command === UnitControlCommands.Stop) draft.optimisticClickedControlButtons.stop = true;
    if(command === UnitControlCommands.Pause) draft.optimisticClickedControlButtons.pause = true;
    if(command === UnitControlCommands.Unpause) draft.optimisticClickedControlButtons.pause = true;
    if(command === UnitControlCommands.Hold) draft.optimisticClickedControlButtons.hold = true;
    if(command === UnitControlCommands.Unhold) draft.optimisticClickedControlButtons.hold = true;
  })),
  on(DetailsActions.controlCommandExecutionFailed, state => produce(state, draft => {
    draft.optimisticClickedControlButtons = {start: false, stop: false, pause: false, hold: false};
  })),
);

export const detailsSlice = {name: 'details', reducer};
