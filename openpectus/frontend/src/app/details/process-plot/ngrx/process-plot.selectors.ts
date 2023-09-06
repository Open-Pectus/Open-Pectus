import { createFeatureSelector, createSelector } from '@ngrx/store';
import { processPlotSlice, ProcessPlotState } from './process-plot.reducer';

export class ProcessPlotSelectors {
  static selectFeature = createFeatureSelector<ProcessPlotState>(processPlotSlice.name);
  static plotConfiguration = createSelector(this.selectFeature, state => state.plotConfiguration);
  static processValuesLog = createSelector(this.selectFeature, state => state.processValuesLog);
  static zoomedSubplotIndices = createSelector(this.selectFeature, state => state.zoomedSubplotIndices);
  static anySubplotZoomed = createSelector(this.zoomedSubplotIndices, zoomedSubplotIndices => zoomedSubplotIndices.length !== 0);
  static markedDirty = createSelector(this.selectFeature, state => state.markedDirty);
  static yAxisOverrideDialogData = createSelector(this.selectFeature, state => state.yAxisOverrideDialogData);
  static yAxesLimitsOverride = createSelector(this.selectFeature, state => state.yAxesLimitsOverride);
  static zoomAndPanDomainOverrides = createSelector(this.selectFeature, state => state.zoomAndPanDomainOverrides);
  static plotIsModified = createSelector(this.anySubplotZoomed, this.yAxesLimitsOverride, (isZoomed, yAxisOverrides) => {
    return isZoomed || yAxisOverrides !== undefined;
  });
}
