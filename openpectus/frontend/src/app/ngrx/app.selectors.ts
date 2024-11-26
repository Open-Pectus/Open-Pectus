import { createFeatureSelector, createSelector } from '@ngrx/store';
import { appFeatureKey, AppState } from './app.reducer';

export class AppSelectors {
  static selectFeature = createFeatureSelector<AppState>(appFeatureKey);
  static processUnits = createSelector(this.selectFeature, state => state.processUnits);
  static authIsEnabled = createSelector(this.selectFeature, state => state.authIsEnabled);
  static webSocketIsDisconnected = createSelector(this.selectFeature, state => state.webSocketIsDisconnected);
  static buildInfo = createSelector(this.selectFeature, state => state.buildInfo);
  static userData = createSelector(this.selectFeature, state => state.userData);
  static userPicture = createSelector(this.selectFeature, state => state.userPicture);
}
