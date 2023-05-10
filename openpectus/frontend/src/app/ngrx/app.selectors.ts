import { createFeatureSelector, createSelector } from '@ngrx/store';
import { appFeatureKey, AppState } from './app.reducer';

export class AppSelectors {
  static selectFeature = createFeatureSelector<AppState>(appFeatureKey);
  static processUnits = createSelector(this.selectFeature,
    state => state.processUnits,
  );
}
