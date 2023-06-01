import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { ProcessUnit } from '../api';
import { AppActions } from './app.actions';

export const appFeatureKey = 'app';

export interface AppState {
  processUnits: ProcessUnit[];
}

const initialState: AppState = {
  processUnits: [],
};

export const appReducer = createReducer(initialState,
  on(AppActions.processUnitsLoaded, (state, {processUnits}) => produce(state, draft => {
    draft.processUnits = processUnits;
  })),
);

