import { createReducer, on } from '@ngrx/store';
import produce from 'immer';
import { ProcessUnit } from '../api';
import { DashboardActions } from './dashboard.actions';

export const dashboardFeatureKey = 'dashboard';

export interface DashboardState {
  processUnits: ProcessUnit[];
  recentBatchJobFilter: string;
}

const initialState: DashboardState = {
  processUnits: [],
  recentBatchJobFilter: '',
};

export const dashboardReducer = createReducer(initialState,
  on(DashboardActions.processUnitsLoaded, (state, {processUnits}) => produce(state, draft => {
    draft.processUnits = processUnits;
  })),
  on(DashboardActions.recentBatchJobFilterChanged, (state, {filter}) => produce(state, draft => {
    draft.recentBatchJobFilter = filter;
  })),
);

