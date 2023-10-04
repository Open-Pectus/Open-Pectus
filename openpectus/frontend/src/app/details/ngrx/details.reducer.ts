import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { CommandExample, ControlState, ProcessDiagram, ProcessValue } from '../../api';
import { DetailsActions } from './details.actions';

export interface DetailsState {
  processValues: ProcessValue[];
  processDiagram?: ProcessDiagram;
  shouldPollProcessValues: boolean;
  commandExamples: CommandExample[];
  controlState: ControlState;
}

const initialState: DetailsState = {
  processValues: [],
  shouldPollProcessValues: false,
  commandExamples: [],
  controlState: {
    is_running: false,
    is_holding: false,
    is_paused: false,
  },
};

const reducer = createReducer(initialState,
  on(DetailsActions.unitDetailsInitialized, state => produce(state, draft => {
    draft.shouldPollProcessValues = true;
  })),
  on(DetailsActions.unitDetailsDestroyed, state => produce(state, draft => {
    draft.shouldPollProcessValues = false;
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
);

export const detailsSlice = {name: 'details', reducer};
