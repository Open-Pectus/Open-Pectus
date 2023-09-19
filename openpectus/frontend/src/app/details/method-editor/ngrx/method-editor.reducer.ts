import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
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
  on(MethodEditorActions.methodFetched, (state, {method}) => produce(state, draft => {
    draft.methodEditorIsDirty = false;
    draft.methodEditorContent = method.content;
  })),
  on(MethodEditorActions.monacoEditorComponentInitialized, state => produce(state, draft => {
    draft.monacoServicesInitialized = true;
  })),
  on(MethodEditorActions.monacoEditorComponentDestroyed, state => produce(state, draft => {
    draft.methodEditorContent = undefined;
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
