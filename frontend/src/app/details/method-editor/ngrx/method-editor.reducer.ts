import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { Method, MethodState } from '../../../api';
import { UtilMethods } from '../../../shared/util-methods';
import { MethodEditorActions } from './method-editor.actions';

export interface MethodEditorState {
  isDirty: boolean;
  versionMismatch: boolean;
  method: Method;
  methodState: MethodState;
}

const initialState: MethodEditorState = {
  isDirty: false,
  versionMismatch: false,
  method: {lines: [], version: 0, last_author: ''},
  methodState: {
    started_line_ids: [],
    executed_line_ids: [],
    injected_line_ids: [],
  },
};

const reducer = createReducer(initialState,
  on(MethodEditorActions.methodEditorComponentDestroyed, () => {
    return {...initialState};
  }),
  on(MethodEditorActions.methodFetchedInitially, (state, {methodAndState}) => produce(state, draft => {
    draft.isDirty = false;
    draft.method = methodAndState.method;
    draft.methodState = methodAndState.state;
  })),
  on(MethodEditorActions.methodFetchedDueToUpdate, (state, {method}) => produce(state, draft => {
    if(state.isDirty) {
      draft.versionMismatch = true;
    } else {
      draft.method = method;
    }
  })),
  on(MethodEditorActions.methodStateFetchedDueToUpdate, (state, {methodAndState}) => produce(state, draft => {
    if(!UtilMethods.arrayEquals(draft.methodState.executed_line_ids, methodAndState.state.executed_line_ids)) {
      draft.methodState.executed_line_ids = methodAndState.state.executed_line_ids;
    }
    if(!UtilMethods.arrayEquals(draft.methodState.injected_line_ids, methodAndState.state.injected_line_ids)) {
      draft.methodState.injected_line_ids = methodAndState.state.injected_line_ids;
    }
    if(!UtilMethods.arrayEquals(draft.methodState.started_line_ids, methodAndState.state.started_line_ids)) {
      draft.methodState.started_line_ids = methodAndState.state.started_line_ids;
    }

    const lockedLineIds = methodAndState.state.executed_line_ids.concat(methodAndState.state.started_line_ids);
    lockedLineIds.forEach((lockedLineId) => {
      const oldLine = draft.method.lines.find(line => line.id === lockedLineId);
      const newLineIndex = methodAndState.method.lines.findIndex(line => line.id === lockedLineId);
      const newLine = methodAndState.method.lines[newLineIndex];
      if(newLine === undefined) {
        console.warn('Backend designated a non-existing line id as executed! This is fine if you\'re using MSW.');
        return;
      }
      if(oldLine === undefined) {
        draft.method.lines.splice(newLineIndex, 0, newLine);
      } else {
        oldLine.content = newLine.content;
      }
    });
  })),
  on(MethodEditorActions.modelSaved, (state, {newVersion}) => produce(state, draft => {
    draft.isDirty = false;
    draft.method.version = newVersion;
  })),
  on(MethodEditorActions.linesChanged, (state, {lines}) => produce(state, draft => {
    draft.isDirty = true;
    draft.method.lines = lines;
  })),
  on(MethodEditorActions.saveButtonClicked, (state) => produce(state, draft => {
    const lastLine = state.method.lines.at(-1);
    if(lastLine?.content.trim() !== '') {
      draft.method.lines.push({
        id: crypto.randomUUID(),
        content: '',
      });
    }
  })),
);

export const methodEditorSlice = {name: 'methodEditor', reducer};
