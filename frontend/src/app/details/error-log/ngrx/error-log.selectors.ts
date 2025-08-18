import { createFeatureSelector, createSelector } from '@ngrx/store';
import { errorLogSlice, ErrorLogState } from './error-log.reducer';

export class ErrorLogSelectors {
  static selectFeature = createFeatureSelector<ErrorLogState>(errorLogSlice.name);
  static errorLog = createSelector(this.selectFeature, state => state.errorLog);
}
