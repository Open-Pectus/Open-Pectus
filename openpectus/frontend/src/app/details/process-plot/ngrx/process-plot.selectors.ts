import { createFeatureSelector, createSelector } from '@ngrx/store';
import { UtilMethods } from '../../../shared/util-methods';
import { processPlotSlice, ProcessPlotState } from './process-plot.reducer';

export class ProcessPlotSelectors {
  static selectFeature = createFeatureSelector<ProcessPlotState>(processPlotSlice.name);
  static plotConfiguration = createSelector(this.selectFeature, state => state.plotConfiguration);
  static processValuesLog = createSelector(this.selectFeature, state => state.processValuesLog);
  static markedDirty = createSelector(this.selectFeature, state => state.markedDirty);
  static yAxisOverrideDialogData = createSelector(this.selectFeature, state => state.yAxisOverrideDialogData);
  static yAxesLimitsOverride = createSelector(this.selectFeature, state => state.yAxesLimitsOverride);
  static zoomAndPanDomainOverrides = createSelector(this.selectFeature, state => state.zoomAndPanDomainOverrides);
  static zoomedSubplotIndices = createSelector(this.zoomAndPanDomainOverrides, overrides => {
    if(overrides === undefined) return [];
    return overrides.y.map((override, index) => override === null ? null : index).filter(UtilMethods.isNotNullOrUndefined);
  });
  static anySubplotZoomed = createSelector(this.zoomedSubplotIndices, zoomedSubplotIndices => zoomedSubplotIndices.length !== 0);
  static xAxisProcessValueOverride = createSelector(this.selectFeature, state => state.xAxisProcessValueOverride);
  static plotIsModified = createSelector(this.anySubplotZoomed, this.yAxesLimitsOverride, this.xAxisProcessValueOverride,
    (isZoomed, yAxisOverrides, xAxisOverride) => {
      return isZoomed || yAxisOverrides !== undefined || xAxisOverride !== undefined;
    });
  static xAxisOverrideDialogData = createSelector(this.selectFeature, state => state.xAxisOverrideDialogData);
  static xAxisProcessValueCandidates = createSelector(this.plotConfiguration,
    plotConfiguration => plotConfiguration?.x_axis_process_value_names);
  static xAxisProcessValueName = createSelector(this.plotConfiguration, this.xAxisProcessValueOverride, (plotConfiguration, override) => {
    return override ?? plotConfiguration?.x_axis_process_value_names[0];
  });
}
