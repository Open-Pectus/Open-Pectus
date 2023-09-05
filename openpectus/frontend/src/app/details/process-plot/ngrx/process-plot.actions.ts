import { createAction, props } from '@ngrx/store';
import { PlotConfiguration } from '../../../api';
import { YAxisLimits, YAxisOverrideDialogData } from '../process-plot-d3.types';

const source = '[Process Plot] ';

export class ProcessPlotActions {
  static processPlotComponentInitialized = createAction(source + 'Process Plot Component Initialized');
  static plotConfigurationFetched = createAction(source + 'Plot Configuration Fetched', props<{ configuration: PlotConfiguration }>());
  static processPlotZoomed = createAction(source + 'Process Plot Zoomed', props<{ subPlotIndex: number }>());
  static processPlotZoomReset = createAction(source + 'Process Plot Zoom Reset');
  static processPlotElementsPlaced = createAction(source + 'Process Plot Elements Placed');
  static processPlotAxesUpdated = createAction(source + 'Process Plot Axes Updated');
  static processPlotResized = createAction(source + 'Process Plot Resized');
  static newAnnotatedValueAppeared = createAction(source + 'New Annotated Value appeared');
  static processPlotInitialized = createAction(source + 'Process Plot Initialized');
  static processPlotPanned = createAction(source + 'Process Plot Panned');
  static yAxisClicked = createAction(source + 'Y Axis Clicked', props<{ data: YAxisOverrideDialogData }>());
  static yOverrideDialogClosed = createAction(source + 'Y Axis Override Dialog Closed');
  static yOverrideDialogSaveClicked = createAction(source + 'Y Axis Override Dialog Save Clicked',
    props<{ subplotIndex: number, axisIndex: number, limits: YAxisLimits }>());
}
