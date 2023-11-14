import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { BatchJob, CommandExample, ControlState, ProcessDiagram, ProcessValue } from '../../api';
import { DetailsActions } from './details.actions';

export interface DetailsState {
  processValues: ProcessValue[];
  processDiagram?: ProcessDiagram;
  commandExamples: CommandExample[];
  controlState: ControlState;
  batchJob?: BatchJob;
  shouldPoll: boolean;
}

const initialState: DetailsState = {
  processValues: [],
  commandExamples: [],
  shouldPoll: false,
  controlState: {
    is_running: false,
    is_holding: false,
    is_paused: false,
  },
};

const reducer = createReducer(initialState,
  on(DetailsActions.unitDetailsInitialized, state => produce(state, draft => {
    draft.shouldPoll = true;
  })),
  on(DetailsActions.unitDetailsDestroyed, state => produce(state, draft => {
    draft.shouldPoll = false;
  })),
  on(DetailsActions.processValuesFetched, (state, {processValues}) => produce(state, draft => {
    draft.processValues = processValues;
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
  on(DetailsActions.batchJobFetched, (state, {batchJob}) => produce(state, draft => {
    draft.batchJob = batchJob;
  })),
);

export const detailsSlice = {name: 'details', reducer};
