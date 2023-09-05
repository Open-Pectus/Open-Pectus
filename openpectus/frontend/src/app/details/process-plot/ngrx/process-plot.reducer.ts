import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { PlotConfiguration, ProcessValue } from '../../../api';
import { DetailsActions } from '../../ngrx/details.actions';
import { YAxisLimits, YAxisOverrideDialogData } from '../process-plot-d3.types';
import { ProcessPlotActions } from './process-plot.actions';

export type ProcessValueLog = Record<string, ProcessValue[]>

export interface ProcessPlotState {
  plotConfiguration?: PlotConfiguration;
  processValuesLog: ProcessValueLog;
  zoomedSubplotIndices: number[];
  markedDirty: boolean;
  scalesMarkedDirty: boolean;
  yAxisOverrideDialogData?: YAxisOverrideDialogData;
  xAxisProcessValueOverride?: string;
  yAxesLimitsOverride?: YAxisLimits[][];
}

const initialState: ProcessPlotState = {
  processValuesLog: {},
  zoomedSubplotIndices: [],
  markedDirty: false,
  scalesMarkedDirty: false,
};

const reducer = createReducer(initialState,
  on(ProcessPlotActions.plotConfigurationFetched, (state, {configuration}) => produce(state, draft => {
    draft.plotConfiguration = configuration;
  })),
  on(ProcessPlotActions.processPlotZoomed, (state, {subPlotIndex}) => produce(state, draft => {
    draft.zoomedSubplotIndices.push(subPlotIndex);
  })),
  on(ProcessPlotActions.processPlotZoomReset, (state) => produce(state, draft => {
    draft.zoomedSubplotIndices = [];
  })),
  on(ProcessPlotActions.processPlotElementsPlaced, state => produce(state, draft => {
    draft.markedDirty = false;
  })),
  on(ProcessPlotActions.processPlotAxesUpdated, state => produce(state, draft => {
    draft.scalesMarkedDirty = false;
  })),
  on(
    ProcessPlotActions.processPlotResized,
    ProcessPlotActions.newAnnotatedValueAppeared,
    ProcessPlotActions.processPlotInitialized,
    ProcessPlotActions.processPlotZoomReset,
    state => produce(state, draft => {
      draft.markedDirty = true;
    })),
  on(ProcessPlotActions.processPlotZoomed,
    ProcessPlotActions.processPlotPanned,
    state => produce(state, draft => {
      draft.scalesMarkedDirty = true;
    })),
  on(DetailsActions.processValuesFetched, (state, {processValues}) => produce(state, draft => {
    processValues.forEach(processValue => {
      const existing = draft.processValuesLog[processValue.name];
      if(existing === undefined) {
        draft.processValuesLog[processValue.name] = [processValue];
      } else {
        existing.push(processValue);
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
    draft.scalesMarkedDirty = true;
  })),
);

export const processPlotSlice = {name: 'processPlot', reducer};
