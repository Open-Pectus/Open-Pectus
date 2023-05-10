import { createReducer, on } from '@ngrx/store';
import produce from 'immer';
import { ProcessDiagram, ProcessValue } from '../../api';
import { DetailsActions } from './details.actions';

export const detailsFeatureKey = 'details';

export interface DetailsState {
  methodEditorIsDirty: boolean;
  methodEditorContent?: string;
  processValues: ProcessValue[];
  processDiagram?: ProcessDiagram;
}

const initialState: DetailsState = {
  methodEditorIsDirty: false,
  processValues: [],
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
  on(DetailsActions.processValuesLoaded, (state, {processValues}) => produce(state, draft => {
    draft.processValues = processValues;
  })),
  on(DetailsActions.processDiagramFetched, (state, {processDiagram}) => produce(state, draft => {
    draft.processDiagram = processDiagram;
  })),
);

