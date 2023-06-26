import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { CommandExample, ProcessDiagram, ProcessValue } from '../../api';
import { DetailsActions } from './details.actions';

export interface DetailsState {
  processValues: ProcessValue[];
  processValuesLog: ProcessValue[][];
  processDiagram?: ProcessDiagram;
  shouldPollProcessValues: boolean;
  commandExamples: CommandExample[];
}

const initialState: DetailsState = {
  processValues: [],
  processValuesLog: [],
  shouldPollProcessValues: false,
  commandExamples: [],
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
    draft.processValuesLog.push(processValues);
  })),
  on(DetailsActions.processDiagramFetched, (state, {processDiagram}) => produce(state, draft => {
    draft.processDiagram = processDiagram;
  })),
  on(DetailsActions.commandExamplesFetched, (state, {commandExamples}) => produce(state, draft => {
    draft.commandExamples = commandExamples;
  })),
);

export const detailsSlice = {name: 'details', reducer};
