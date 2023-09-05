import { createFeatureSelector, createSelector } from '@ngrx/store';
import { produce } from 'immer';
import { processPlotSlice, ProcessPlotState } from './process-plot.reducer';

export class ProcessPlotSelectors {
  static selectFeature = createFeatureSelector<ProcessPlotState>(processPlotSlice.name);
  static rawPlotConfiguration = createSelector(this.selectFeature, state => state.plotConfiguration);
  static processValuesLog = createSelector(this.selectFeature, state => state.processValuesLog);
  static zoomedSubplotIndices = createSelector(this.selectFeature, state => state.zoomedSubplotIndices);
  static anySubplotZoomed = createSelector(this.zoomedSubplotIndices, zoomedSubplotIndices => zoomedSubplotIndices.length !== 0);
  static markedDirty = createSelector(this.selectFeature, state => state.markedDirty);
  static scalesMarkedDirty = createSelector(this.selectFeature, state => state.scalesMarkedDirty);
  static yAxisOverrideDialogData = createSelector(this.selectFeature, state => state.yAxisOverrideDialogData);
  static yAxesLimitsOverride = createSelector(this.selectFeature, state => state.yAxesLimitsOverride);
  static plotConfiguration = createSelector(this.rawPlotConfiguration, this.yAxesLimitsOverride,
    (plotConfiguration, yAxesLimitsOverride) => {
      if(plotConfiguration === undefined) return;
      if(yAxesLimitsOverride === undefined) return plotConfiguration;
      return produce(plotConfiguration, draft => {
        yAxesLimitsOverride?.forEach((subplotOverride, subplotIndex) => {
          subplotOverride.forEach((axisOverride, axisIndex) => {
            if(axisOverride === null) return;
            draft.sub_plots[subplotIndex].axes[axisIndex].y_min = axisOverride.yMin;
            draft.sub_plots[subplotIndex].axes[axisIndex].y_max = axisOverride.yMax;
          });
        });
      });
    });
}
