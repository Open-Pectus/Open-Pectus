import { createReducer, on } from '@ngrx/store';
import produce from 'immer';
import { DetailsActions } from './details.actions';

export const detailsFeatureKey = 'dashboard';

export interface DetailsState {
  methodEditorIsDirty: boolean;
  methodEditorContent: string;
}

const initialState: DetailsState = {
  methodEditorIsDirty: false,
  methodEditorContent: '',
};

export const detailsReducer = createReducer(initialState,
  on(DetailsActions.methodEditorModelSaved, state => produce(state, draft => {
    draft.methodEditorIsDirty = false;
  })),
  on(DetailsActions.methodEditorModelChanged, (state, {model}) => produce(state, draft => {
    draft.methodEditorIsDirty = true;
    draft.methodEditorContent = model;
  })),
);

