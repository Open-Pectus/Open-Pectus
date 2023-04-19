import { createFeatureSelector } from '@ngrx/store';
import { appFeatureKey, AppState } from './app.reducer';

export class AppSelectors {
  static selectFeature = createFeatureSelector<AppState>(appFeatureKey);
}
