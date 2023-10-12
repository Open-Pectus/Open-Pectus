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
}

const initialState: DetailsState = {
  processValues: [],
  commandExamples: [],
  controlState: {
    is_running: false,
    is_holding: false,
    is_paused: false,
  },
};

const reducer = createReducer(initialState,
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
  on(DetailsActions.processUnitCommandButtonClicked, (state, {command}) => produce(state, draft => {
    switch(command) {
      case 'Start':
        draft.controlState.is_running = true;
        break;
      case 'Pause':
        draft.controlState.is_paused = true;
        break;
      case 'Unpause':
        draft.controlState.is_paused = false;
        break;
      case 'Hold':
        draft.controlState.is_holding = true;
        break;
      case 'Unhold':
        draft.controlState.is_holding = false;
        break;
      case 'Stop':
        draft.controlState.is_running = false;
        break;
    }
  })),
  on(DetailsActions.batchJobFetched, (state, {batchJob}) => produce(state, draft => {
    draft.batchJob = batchJob;
  })),
);

export const detailsSlice = {name: 'details', reducer};
