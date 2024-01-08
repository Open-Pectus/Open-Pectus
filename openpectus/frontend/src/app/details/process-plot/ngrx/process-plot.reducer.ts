import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { PlotConfiguration, PlotLog, PlotLogEntry } from '../../../api';
import { DetailsActions } from '../../ngrx/details.actions';
import { XAxisOverrideDialogData, YAxesLimitsOverride, YAxisOverrideDialogData, ZoomAndPanDomainOverrides } from '../process-plot.types';
import { ProcessPlotActions } from './process-plot.actions';

export interface ProcessPlotState {
  plotConfiguration?: PlotConfiguration;
  plotLog: PlotLog;
  markedDirty: boolean;
  yAxisOverrideDialogData?: YAxisOverrideDialogData;
  xAxisProcessValueOverride?: string;
  yAxesLimitsOverride?: YAxesLimitsOverride;
  zoomAndPanDomainOverrides?: ZoomAndPanDomainOverrides;
  xAxisOverrideDialogData?: XAxisOverrideDialogData;
}

const initialState: ProcessPlotState = {
  plotLog: {entries: {}},
  markedDirty: false,
};

const reducer = createReducer(initialState,
  on(ProcessPlotActions.processPlotComponentDestroyed, () => initialState),
  on(ProcessPlotActions.plotConfigurationFetched, (state, {configuration}) => produce(state, draft => {
    draft.plotConfiguration = configuration;
  })),
  on(ProcessPlotActions.processPlotZoomed,
    ProcessPlotActions.processPlotPanned,
    (state, {subPlotIndex, newXDomain, newYDomains}) => produce(state, draft => {
      const yDomainOverrides = draft.zoomAndPanDomainOverrides?.y ?? [];
      yDomainOverrides[subPlotIndex] = newYDomains;
      draft.zoomAndPanDomainOverrides = {
        x: newXDomain,
        y: yDomainOverrides,
      };
    })),
  on(ProcessPlotActions.processPlotZoomReset,
    ProcessPlotActions.processPlotReset,
    (state) => produce(state, draft => {
      draft.zoomAndPanDomainOverrides = undefined;
    })),
  on(ProcessPlotActions.processPlotElementsPlaced, state => produce(state, draft => {
    draft.markedDirty = false;
  })),
  on(
    ProcessPlotActions.processPlotResized,
    ProcessPlotActions.newAnnotatedValueAppeared,
    ProcessPlotActions.processPlotInitialized,
    ProcessPlotActions.processPlotZoomReset,
    ProcessPlotActions.processPlotReset,
    ProcessPlotActions.plotLogFetched,
    state => produce(state, draft => {
      draft.markedDirty = true;
    })),
  on(DetailsActions.processValuesFetched, (state, {processValues}) => produce(state, draft => {
    processValues.forEach(processValue => {
      const existing = draft.plotLog.entries[processValue.name];
      if(existing === undefined) {
        draft.plotLog.entries[processValue.name] = {
          name: processValue.name,
          value_unit: processValue.value_unit,
          value_type: processValue.value_type,
          values: [{value: processValue.value, timestamp_ms: Date.now()}],
        };
      } else {
        existing.values.push({value: processValue.value, timestamp_ms: Date.now()});
      }
    });
  })),
  on(ProcessPlotActions.yAxisClicked, (state, {data}) => produce(state, draft => {
    draft.yAxisOverrideDialogData = data;
  })),
  on(ProcessPlotActions.yOverrideDialogClosed, (state) => produce(state, draft => {
    draft.yAxisOverrideDialogData = undefined;
  })),
  on(ProcessPlotActions.yOverrideDialogSaveClicked, (state, {subplotIndex, axisIndex, limits}) => produce(state, draft => {
    if(draft.yAxesLimitsOverride === undefined) draft.yAxesLimitsOverride = [];
    if(draft.yAxesLimitsOverride[subplotIndex] === undefined) draft.yAxesLimitsOverride[subplotIndex] = [];
    draft.yAxesLimitsOverride[subplotIndex][axisIndex] = limits;
    draft.yAxisOverrideDialogData = undefined;
  })),
  on(ProcessPlotActions.yAxesOverrideLimitsRestoredFromLocalStorage, (state, {yAxesLimitsOverride}) => produce(state, draft => {
    draft.yAxesLimitsOverride = yAxesLimitsOverride;
  })),
  on(ProcessPlotActions.xAxisProcessValueNameRestoredFromLocalStorage, (state, {xAxisProcessValueName}) => produce(state, draft => {
    draft.xAxisProcessValueOverride = xAxisProcessValueName;
  })),
  on(ProcessPlotActions.processPlotReset, state => produce(state, draft => {
    draft.yAxesLimitsOverride = undefined;
    draft.xAxisProcessValueOverride = undefined;
  })),
  on(ProcessPlotActions.xAxisClicked, (state, {data}) => produce(state, draft => {
    draft.xAxisOverrideDialogData = data;
  })),
  on(ProcessPlotActions.xOverrideDialogSaveClicked, (state, {processValueName}) => produce(state, draft => {
    draft.xAxisProcessValueOverride = processValueName;
    draft.xAxisOverrideDialogData = undefined;
  })),
  on(ProcessPlotActions.xOverrideDialogClosed, (state) => produce(state, draft => {
    draft.xAxisOverrideDialogData = undefined;
  })),
  on(ProcessPlotActions.plotLogFetched, (state, {plotLog}) => produce(state, draft => {
    const requiredTimestamps = Object.values(plotLog.entries)
      .filter(entry => state.plotConfiguration?.x_axis_process_value_names.includes(entry.name))
      .flatMap(entry => entry.values.map(value => value.timestamp_ms));
    const sortedUniqueTimestamps = [...new Set(requiredTimestamps)].sort((a, b) => a - b);
    const newEntries: Record<string, PlotLogEntry> = {};
    Object.entries(plotLog.entries).forEach(([name, entry]) => {
      if(entry.values.length === 0) return; // skip empty entries
      const newValues = sortedUniqueTimestamps.map(requiredTimestamp => {
        const bestMatchingValue = entry.values.reduce((prev, curr) => {
          if(curr.timestamp_ms > requiredTimestamp) return prev;
          if(curr.timestamp_ms > prev.timestamp_ms) return curr;
          return prev;
        });
        return {value: bestMatchingValue.value, timestamp_ms: requiredTimestamp};
      });
      newEntries[name] = {...entry, values: newValues};
    });
    draft.plotLog.entries = newEntries;
  })),
);

export const processPlotSlice = {name: 'processPlot', reducer};
