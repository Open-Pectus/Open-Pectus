import { createAction, props } from '@ngrx/store';
import { PlotConfiguration } from '../../../api/models/PlotConfiguration';
import { PlotLog } from '../../../api/models/PlotLog';
import { ProcessValue } from '../../../api/models/ProcessValue';
import { AxisLimits, XAxisOverrideDialogData, YAxesLimitsOverride, YAxisOverrideDialogData } from '../process-plot.types';

const source = '[Process Plot] ';

export class ProcessPlotActions {
  static processPlotComponentInitializedForUnit = createAction(source + 'Process Plot Component Initialized For Unit',
    props<{ unitId: string }>());
  static processPlotComponentInitializedForRecentRun = createAction(source + 'Process Plot Component Initialized For Recent Run',
    props<{ recentRunId: string }>());
  static processValuesFetched = createAction(source + 'Process Values Fetched', props<{ processValues: ProcessValue[] }>());
  static processPlotComponentDestroyed = createAction(source + 'Process Plot Component Destroyed');
  static plotConfigurationFetched = createAction(source + 'Plot Configuration Fetched', props<{ configuration: PlotConfiguration }>());
  static processPlotZoomed = createAction(source + 'Process Plot Zoomed',
    props<{ subPlotIndex: number, newXDomain: AxisLimits, newYDomains: AxisLimits[] }>());
  static processPlotZoomReset = createAction(source + 'Process Plot Zoom Reset');
  static processPlotElementsPlaced = createAction(source + 'Process Plot Elements Placed');
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
  static xAxisProcessValueNameRestoredFromLocalStorage = createAction(source + 'X Axes Process Value Name Restored From LocalStorage',
    props<{ xAxisProcessValueName: string }>());
  static processPlotReset = createAction(source + 'Process Plot Reset');
  static xAxisClicked = createAction(source + 'X Axis Clicked', props<{ data: XAxisOverrideDialogData }>());
  static xOverrideDialogClosed = createAction(source + 'X Axis Override Dialog Closed');
  static xOverrideDialogSaveClicked = createAction(source + 'X Axis Override Dialog Save Clicked', props<{ processValueName: string }>());
  static plotLogFetched = createAction(source + 'Plot Log Fetched', props<{ plotLog: PlotLog }>());
}
