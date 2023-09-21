import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { Method } from '../../../api';
import { MethodEditorActions } from './method-editor.actions';

export interface MethodEditorState {
  monacoServicesInitialized: boolean;
  isDirty: boolean;
  method: Method;
}

const initialState: MethodEditorState = {
  monacoServicesInitialized: false,
  isDirty: false,
  method: {lines: []},
};

const reducer = createReducer(initialState,
  on(MethodEditorActions.methodFetched, (state, {method}) => produce(state, draft => {
    draft.isDirty = false;
    draft.method = method;
  })),
  on(MethodEditorActions.methodPolled, (state, {method}) => produce(state, draft => {
    method.lines.forEach((newLine, newLineIndex) => {
      const oldLine = draft.method.lines.find(line => line.id === newLine.id);
      if(oldLine === undefined) {
        if(newLine.is_locked) draft.method.lines.splice(newLineIndex, 0, newLine);
      } else {
        oldLine.is_locked = newLine.is_locked;
        oldLine.is_injected = newLine.is_injected;
        if(newLine.is_locked) oldLine.content = newLine.content;
      }
    });
  })),
  on(MethodEditorActions.monacoEditorComponentInitialized, state => produce(state, draft => {
    draft.monacoServicesInitialized = true;
  })),
  on(MethodEditorActions.monacoEditorComponentDestroyed, state => produce(state, draft => {
    draft.method = {lines: []};
  })),
  on(MethodEditorActions.modelSaved, state => produce(state, draft => {
    draft.isDirty = false;
  })),
  on(MethodEditorActions.linesChanged, (state, {lines}) => produce(state, draft => {
    draft.isDirty = true;
    draft.method.lines = lines;
  })),
);

export const methodEditorSlice = {name: 'methodEditor', reducer};
