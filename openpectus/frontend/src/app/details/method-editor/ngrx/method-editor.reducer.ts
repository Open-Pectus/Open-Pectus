import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { Method } from '../../../api';
import { UtilMethods } from '../../../shared/util-methods';
import { MethodEditorActions } from './method-editor.actions';

export interface MethodEditorState {
  monacoServicesInitialized: boolean;
  isDirty: boolean;
  method: Method;
}

const initialState: MethodEditorState = {
  monacoServicesInitialized: false,
  isDirty: false,
  method: {
    lines: [],
    executed_line_ids: [],
    injected_line_ids: [],
  },
};

const reducer = createReducer(initialState,
  on(MethodEditorActions.methodFetched, (state, {method}) => produce(state, draft => {
    draft.isDirty = false;
    draft.method = method;
  })),
  on(MethodEditorActions.methodPolled, (state, {method}) => produce(state, draft => {
    if(!UtilMethods.arrayEquals(draft.method.executed_line_ids, method.executed_line_ids)) {
      draft.method.executed_line_ids = method.executed_line_ids;
    }
    if(!UtilMethods.arrayEquals(draft.method.injected_line_ids, method.injected_line_ids)) {
      draft.method.injected_line_ids = method.injected_line_ids;
    }

    // take content only from executed (and therefore locked) lines.
    method.executed_line_ids.forEach((executedLineId) => {
      const oldLine = draft.method.lines.find(line => line.id === executedLineId);
      const newLineIndex = method.lines.findIndex(line => line.id === executedLineId);
      const newLine = method.lines[newLineIndex];
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
  on(MethodEditorActions.monacoEditorComponentInitialized, state => produce(state, draft => {
    draft.monacoServicesInitialized = true;
  })),
  on(MethodEditorActions.monacoEditorComponentDestroyed, state => produce(state, draft => {
    draft.method = {
      lines: [],
      executed_line_ids: [],
      injected_line_ids: [],
    };
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
