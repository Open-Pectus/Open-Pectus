import { createFeatureSelector, createSelector } from '@ngrx/store';
import { dashboardSlice, DashboardState } from './dashboard.reducer';

export class DashboardSelectors {
  static selectFeature = createFeatureSelector<DashboardState>(dashboardSlice.name);
  static recentBatchJobFilter = createSelector(this.selectFeature, state => state.recentBatchJobFilter);
  static recentBatchJobs = createSelector(this.selectFeature, state => state.recentBatchJobs);
}
