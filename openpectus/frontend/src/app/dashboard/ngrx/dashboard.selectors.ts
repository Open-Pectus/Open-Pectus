import { createFeatureSelector, createSelector } from '@ngrx/store';
import { dashboardSlice, DashboardState } from './dashboard.reducer';

export class DashboardSelectors {
  static selectFeature = createFeatureSelector<DashboardState>(dashboardSlice.name);
  static recentRunsFilter = createSelector(this.selectFeature, state => state.recentRunsFilter);
  static recentRuns = createSelector(this.selectFeature, state => state.recentRuns);
}
