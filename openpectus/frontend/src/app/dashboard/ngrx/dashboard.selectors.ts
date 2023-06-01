import { createFeatureSelector, createSelector } from '@ngrx/store';
import { dashboardFeatureKey, DashboardState } from './dashboard.reducer';

export class DashboardSelectors {
  static selectFeature = createFeatureSelector<DashboardState>(dashboardFeatureKey);
  static recentBatchJobFilter = createSelector(this.selectFeature, state => state.recentBatchJobFilter);
  static recentBatchJobs = createSelector(this.selectFeature, state => state.recentBatchJobs);
}
