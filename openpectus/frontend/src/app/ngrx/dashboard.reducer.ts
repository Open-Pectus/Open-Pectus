import { createReducer, on } from '@ngrx/store';
import produce from 'immer';
import { DashboardActions } from './dashboard.actions';
import { ProcessUnit } from '../api';

export const dashboardFeatureKey = 'dashboard';

export interface DashboardState {
  processUnits: ProcessUnit[];
}

const initialState: DashboardState = {
  processUnits: [],
};

export const dashboardReducer = createReducer(initialState,
  on(DashboardActions.processUnitsLoaded, (state, {processUnits}) => produce(state, draft => {
    draft.processUnits = processUnits;
  })),
);

