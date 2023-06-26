import { createFeatureSelector, createSelector } from '@ngrx/store';
import { runLogSlice, RunLogState } from './run-log.reducer';

export class RunLogSelectors {
  static selectFeature = createFeatureSelector<RunLogState>(runLogSlice.name);
  static runLog = createSelector(this.selectFeature, state => state.runLog);
}
