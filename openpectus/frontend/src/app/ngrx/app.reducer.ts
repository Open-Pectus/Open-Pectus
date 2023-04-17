import { createReducer, on } from '@ngrx/store';
import { AppActions } from './app.actions';
import produce from 'immer';

export const appFeatureKey = 'app';

export interface AppState {
  someValue: string;
}

const initialState: AppState = {
  someValue: 'test string',
};

export const appReducer = createReducer(initialState,
  on(AppActions.aTestAction, (state, {aString}) => produce(state, draft => {
    draft.someValue = aString;
  }))
);

