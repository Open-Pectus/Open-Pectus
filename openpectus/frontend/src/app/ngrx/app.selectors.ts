import { createFeatureSelector, createSelector } from '@ngrx/store';
import { appFeatureKey, AppState } from './app.reducer';

export class AppSelectors {
  static selectFeature = createFeatureSelector<AppState>(appFeatureKey);
  static processUnits = createSelector(this.selectFeature, state => state.processUnits);
  static authIsEnabled = createSelector(this.selectFeature, state => state.authIsEnabled);
  static webSocketIsDisconnected = createSelector(this.selectFeature, state => state.webSocketIsDisconnected);
}
