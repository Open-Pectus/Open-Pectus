import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { BatchJob } from '../../api';
import { DashboardActions } from './dashboard.actions';

export interface DashboardState {
  recentBatchJobFilter: string;
  recentBatchJobs: BatchJob[];
}

const initialState: DashboardState = {
  recentBatchJobFilter: '',
  recentBatchJobs: [],
};

const reducer = createReducer(initialState,
  on(DashboardActions.recentBatchJobFilterChanged, (state, {filter}) => produce(state, draft => {
    draft.recentBatchJobFilter = filter;
  })),
  on(DashboardActions.recentBatchJobsLoaded, (state, {recentBatchJobs}) => produce(state, draft => {
    draft.recentBatchJobs = recentBatchJobs;
  })),
);

export const dashboardSlice = {name: 'dashboard', reducer};
