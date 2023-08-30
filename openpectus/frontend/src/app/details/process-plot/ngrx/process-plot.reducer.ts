import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { PlotConfiguration, ProcessValue } from '../../../api';
import { DetailsActions } from '../../ngrx/details.actions';
import { ProcessPlotActions } from './process-plot.actions';

export type ProcessValueLog = Record<string, ProcessValue[]>

export interface ProcessPlotState {
  plotConfiguration?: PlotConfiguration;
  processValuesLog: ProcessValueLog;
  zoomed: boolean;
}

const initialState: ProcessPlotState = {
  processValuesLog: {},
  zoomed: false,
};

const reducer = createReducer(initialState,
  on(ProcessPlotActions.plotConfigurationFetched, (state, {configuration}) => produce(state, draft => {
    draft.plotConfiguration = configuration;
  })),
  on(ProcessPlotActions.processPlotZoomed, (state) => produce(state, draft => {
    draft.zoomed = true;
  })),
  on(ProcessPlotActions.processPlotZoomReset, (state) => produce(state, draft => {
    draft.zoomed = false;
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
);

export const processPlotSlice = {name: 'processPlot', reducer};
