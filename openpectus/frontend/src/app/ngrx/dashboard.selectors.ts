import { createFeatureSelector, createSelector } from '@ngrx/store';
import { dashboardFeatureKey, DashboardState } from './dashboard.reducer';

export class DashboardSelectors {
  static selectFeature = createFeatureSelector<DashboardState>(dashboardFeatureKey);
  static processUnits = createSelector(this.selectFeature,
    state => state.processUnits,
  );
}
