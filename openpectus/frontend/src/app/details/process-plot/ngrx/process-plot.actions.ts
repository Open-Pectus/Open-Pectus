import { createAction, props } from '@ngrx/store';
import { PlotConfiguration } from '../../../api';
import { AxisLimits, YAxesLimitsOverride, YAxisOverrideDialogData } from '../process-plot.types';

const source = '[Process Plot] ';

export class ProcessPlotActions {
  static processPlotComponentInitialized = createAction(source + 'Process Plot Component Initialized');
  static plotConfigurationFetched = createAction(source + 'Plot Configuration Fetched', props<{ configuration: PlotConfiguration }>());
  static processPlotZoomed = createAction(source + 'Process Plot Zoomed',
    props<{ subPlotIndex: number, newXDomain: AxisLimits, newYDomains: AxisLimits[] }>());
  static processPlotZoomReset = createAction(source + 'Process Plot Zoom Reset');
  static processPlotElementsPlaced = createAction(source + 'Process Plot Elements Placed');
  static processPlotAxesUpdated = createAction(source + 'Process Plot Axes Updated');
  static processPlotResized = createAction(source + 'Process Plot Resized');
  static newAnnotatedValueAppeared = createAction(source + 'New Annotated Value appeared');
  static processPlotInitialized = createAction(source + 'Process Plot Initialized');
  static processPlotPanned = createAction(source + 'Process Plot Panned',
    props<{ subPlotIndex: number, newXDomain: AxisLimits, newYDomains: AxisLimits[] }>());
  static yAxisClicked = createAction(source + 'Y Axis Clicked', props<{ data: YAxisOverrideDialogData }>());
  static yOverrideDialogClosed = createAction(source + 'Y Axis Override Dialog Closed');
  static yOverrideDialogSaveClicked = createAction(source + 'Y Axis Override Dialog Save Clicked',
    props<{ subplotIndex: number, axisIndex: number, limits: AxisLimits }>());
  static yAxesOverrideLimitsRestoredFromLocalStorage = createAction(source + 'Y Axes Override Limits Restored From LocalStorage',
    props<{ yAxesLimitsOverride: YAxesLimitsOverride }>());
  static processPlotReset = createAction(source + 'Process Plot Reset');
}
