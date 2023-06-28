import { createFeatureSelector, createSelector } from '@ngrx/store';
import { processPlotSlice, ProcessPlotState } from './process-plot.reducer';

export class ProcessPlotSelectors {
  static featureSelector = createFeatureSelector<ProcessPlotState>(processPlotSlice.name);
  static plotConfiguration = createSelector(this.featureSelector, state => state.plotConfiguration);
}
