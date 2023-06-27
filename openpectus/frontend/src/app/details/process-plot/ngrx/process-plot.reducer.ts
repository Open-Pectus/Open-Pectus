import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { PlotConfiguration } from '../../../api';
import { ProcessPlotActions } from './process-plot.actions';

export interface ProcessPlotState {
  plotConfiguration?: PlotConfiguration;
}

const initialState: ProcessPlotState = {};

const reducer = createReducer(initialState,
  on(ProcessPlotActions.plotConfigurationFetched, (state, {configuration}) => produce(state, draft => {
    draft.plotConfiguration = configuration;
  })),
);

export const processPlotSlice = {name: 'processPlot', reducer};
