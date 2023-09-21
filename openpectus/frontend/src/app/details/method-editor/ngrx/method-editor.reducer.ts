import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { MethodEditorActions } from './method-editor.actions';

export interface MethodEditorState {
  monacoServicesInitialized: boolean;
  isDirty: boolean;
  content?: string;
  lockedLines: number[];
  injectedLines: number[];
}

const initialState: MethodEditorState = {
  monacoServicesInitialized: false,
  isDirty: false,
  lockedLines: [],
  injectedLines: [],
};

const reducer = createReducer(initialState,
  on(MethodEditorActions.methodFetched, (state, {method}) => produce(state, draft => {
    draft.isDirty = false;
    draft.content = method.content;
    draft.lockedLines = method.locked_lines;
    draft.injectedLines = method.injected_lines;
  })),
  on(MethodEditorActions.monacoEditorComponentInitialized, state => produce(state, draft => {
    draft.monacoServicesInitialized = true;
  })),
  on(MethodEditorActions.monacoEditorComponentDestroyed, state => produce(state, draft => {
    draft.content = undefined;
  })),
  on(MethodEditorActions.modelSaved, state => produce(state, draft => {
    draft.isDirty = false;
  })),
  on(MethodEditorActions.modelChanged, (state, {model}) => produce(state, draft => {
    draft.isDirty = true;
    draft.content = model;
  })),
);

export const methodEditorSlice = {name: 'methodEditor', reducer};
