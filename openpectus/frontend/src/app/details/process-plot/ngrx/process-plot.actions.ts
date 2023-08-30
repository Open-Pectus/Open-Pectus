import { createAction, props } from '@ngrx/store';
import { PlotConfiguration } from '../../../api';

const source = '[Process Plot] ';

export class ProcessPlotActions {
  static processPlotComponentInitialized = createAction(source + 'Process Plot Component Initialized');
  static processPlotZoomed = createAction(source + 'Process Plot Zoomed');
  static processPlotZoomReset = createAction(source + 'Process Plot Zoom Reset');

  static plotConfigurationFetched = createAction(source + 'Plot Configuration Fetched', props<{ configuration: PlotConfiguration }>());
}
