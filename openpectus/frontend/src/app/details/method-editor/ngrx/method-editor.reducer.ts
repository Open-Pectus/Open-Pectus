import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { DetailsActions } from '../../ngrx/details.actions';
import { MethodEditorActions } from './method-editor.actions';

export interface MethodEditorState {
  monacoServicesInitialized: boolean;
  methodEditorIsDirty: boolean;
  methodEditorContent?: string;
}

const initialState: MethodEditorState = {
  monacoServicesInitialized: false,
  methodEditorIsDirty: false,
};

const reducer = createReducer(initialState,
  on(DetailsActions.unitDetailsInitialized, state => produce(state, draft => {
    // TODO: content should be fetched
    draft.methodEditorIsDirty = false;
    draft.methodEditorContent = `{
"some key": "some value",
"injected": "line",
"another key": "another value",
"another injected": "line"
}`;
  })),
  on(MethodEditorActions.monacoEditorComponentInitialized, state => produce(state, draft => {
    draft.monacoServicesInitialized = true;
  })),
  on(MethodEditorActions.modelSaved, state => produce(state, draft => {
    draft.methodEditorIsDirty = false;
  })),
  on(MethodEditorActions.modelChanged, (state, {model}) => produce(state, draft => {
    draft.methodEditorIsDirty = true;
    draft.methodEditorContent = model;
  })),
);

export const methodEditorSlice = {name: 'methodEditor', reducer};
