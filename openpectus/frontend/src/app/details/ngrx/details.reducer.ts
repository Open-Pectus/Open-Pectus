import { createReducer, on } from '@ngrx/store';
import produce from 'immer';
import { CommandExample, ProcessDiagram, ProcessValue } from '../../api';
import { DetailsActions } from './details.actions';

export const detailsFeatureKey = 'details';

export interface DetailsState {
  methodEditorIsDirty: boolean;
  methodEditorContent?: string;
  processValues: ProcessValue[];
  processDiagram?: ProcessDiagram;
  shouldPollProcessValues: boolean;
  commandExamples: CommandExample[];
}

const initialState: DetailsState = {
  methodEditorIsDirty: false,
  processValues: [],
  shouldPollProcessValues: false,
  commandExamples: [],
};

export const detailsReducer = createReducer(initialState,
  on(DetailsActions.methodEditorInitialized, (state, {model}) => produce(state, draft => {
    draft.methodEditorIsDirty = false;
    draft.methodEditorContent = model;
  })),
  on(DetailsActions.methodEditorModelSaved, state => produce(state, draft => {
    draft.methodEditorIsDirty = false;
  })),
  on(DetailsActions.methodEditorModelChanged, (state, {model}) => produce(state, draft => {
    draft.methodEditorIsDirty = true;
    draft.methodEditorContent = model;
  })),
  on(DetailsActions.processValuesFetched, (state, {processValues}) => produce(state, draft => {
    draft.processValues = processValues;
  })),
  on(DetailsActions.processDiagramFetched, (state, {processDiagram}) => produce(state, draft => {
    draft.processDiagram = processDiagram;
  })),
  on(DetailsActions.processValuesInitialized, (state) => produce(state, draft => {
    draft.shouldPollProcessValues = true;
  })),
  on(DetailsActions.processValuesDestroyed, (state) => produce(state, draft => {
    draft.shouldPollProcessValues = false;
  })),
  on(DetailsActions.commandExamplesFetched, (state, {commandExamples}) => produce(state, draft => {
    draft.commandExamples = commandExamples;
  })),
);

