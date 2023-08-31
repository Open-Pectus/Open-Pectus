import { createAction, props } from '@ngrx/store';
import { PlotConfiguration } from '../../../api';

const source = '[Process Plot] ';

export class ProcessPlotActions {
  static processPlotComponentInitialized = createAction(source + 'Process Plot Component Initialized');
  static processPlotZoomed = createAction(source + 'Process Plot Zoomed');
  static processPlotZoomReset = createAction(source + 'Process Plot Zoom Reset');
  static processPlotElementsPlaced = createAction(source + 'Process Plot Elements Placed');
  static plotConfigurationFetched = createAction(source + 'Plot Configuration Fetched', props<{ configuration: PlotConfiguration }>());
  static processPlotResized = createAction(source + 'Process Plot Resized');
  static newAnnotatedValueAppeared = createAction(source + 'New Annotated Value appeared');
  static processPlotInitialized = createAction(source + 'Process Plot Initialized');
}
