import { createFeatureSelector, createSelector } from '@ngrx/store';
import { processPlotSlice, ProcessPlotState } from './process-plot.reducer';

export class ProcessPlotSelectors {
  static selectFeature = createFeatureSelector<ProcessPlotState>(processPlotSlice.name);
  static plotConfiguration = createSelector(this.selectFeature, state => state.plotConfiguration);
  static processValuesLog = createSelector(this.selectFeature, state => state.processValuesLog);
}
