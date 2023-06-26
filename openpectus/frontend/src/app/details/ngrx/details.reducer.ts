import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { CommandExample, ProcessDiagram, ProcessValue, RunLog } from '../../api';
import { DetailsActions } from './details.actions';

export const detailsFeatureKey = 'details';

export interface DetailsState {
  monacoServicesInitialized: boolean;
  methodEditorIsDirty: boolean;
  methodEditorContent?: string;
  processValues: ProcessValue[];
  processValuesLog: ProcessValue[][];
  processDiagram?: ProcessDiagram;
  shouldPollProcessValues: boolean;
  commandExamples: CommandExample[];
  runLog: RunLog;
}

const initialState: DetailsState = {
  monacoServicesInitialized: false,
  methodEditorIsDirty: false,
  processValues: [],
  processValuesLog: [],
  shouldPollProcessValues: false,
  commandExamples: [],
  runLog: {lines: []},
};

export const detailsReducer = createReducer(initialState,
  on(DetailsActions.unitDetailsInitialized, state => produce(state, draft => {
    draft.shouldPollProcessValues = true;

    // TODO: content should be fetched
    draft.methodEditorIsDirty = false;
    draft.methodEditorContent = `{
  "some key": "some value",
  "injected": "line",
  "another key": "another value",
  "another injected": "line"
}`;
  })),
  on(DetailsActions.unitDetailsDestroyed, state => produce(state, draft => {
    draft.shouldPollProcessValues = false;
  })),
  on(DetailsActions.methodEditorInitialized, state => produce(state, draft => {
    draft.monacoServicesInitialized = true;
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
    draft.processValuesLog.push(processValues);
  })),
  on(DetailsActions.processDiagramFetched, (state, {processDiagram}) => produce(state, draft => {
    draft.processDiagram = processDiagram;
  })),
  on(DetailsActions.commandExamplesFetched, (state, {commandExamples}) => produce(state, draft => {
    draft.commandExamples = commandExamples;
  })),
  on(DetailsActions.runLogFetched, (state, {runLog}) => produce(state, draft => {
    draft.runLog = runLog;
  })),
);

