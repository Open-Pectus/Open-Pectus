import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { RecentRun } from '../../api';
import { DashboardActions } from './dashboard.actions';

export interface DashboardState {
  recentRunsFilter: string;
  recentRuns: RecentRun[];
}

const initialState: DashboardState = {
  recentRunsFilter: '',
  recentRuns: [],
};

const reducer = createReducer(initialState,
  on(DashboardActions.recentRunsFilterChanged, (state, {filter}) => produce(state, draft => {
    draft.recentRunsFilter = filter;
  })),
  on(DashboardActions.recentRunsLoaded, (state, {recentRuns}) => produce(state, draft => {
    draft.recentRuns = recentRuns;
  })),
);

export const dashboardSlice = {name: 'dashboard', reducer};
