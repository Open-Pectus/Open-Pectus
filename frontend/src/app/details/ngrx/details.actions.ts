import { createAction, props } from '@ngrx/store';
import { ActiveUser, ApiError, CommandExample, ControlState, ExecutableCommand, ProcessDiagram, ProcessValue, RecentRun } from '../../api';
import { UnitControlCommands } from '../unit-control-commands.';

const source = '[Details] ';


export class DetailsActions {
  static unitDetailsInitialized = createAction(source + 'Unit Details Initialized', props<{ unitId: string }>());
  static unitDetailsDestroyed = createAction(source + 'Unit Details Destroyed');
  static processValuesFetched = createAction(source + 'Process Values Fetched', props<{ processValues: ProcessValue[] }>());
  static processValuesFailedToLoad = createAction(source + 'Process Values Failed to load', props<{ error: ApiError }>());
  static processUnitCommandButtonClicked = createAction(source + 'Process Unit Command Button Clicked',
    props<{ command: UnitControlCommands }>());
  static processDiagramInitialized = createAction(source + 'Process Diagram Initialized');
  static processDiagramFetched = createAction(source + 'Process Diagram Fetched', props<{ processDiagram: ProcessDiagram }>());
  static commandsComponentInitialized = createAction(source + 'Commands Component Initialized');
  static commandExamplesFetched = createAction(source + 'Command Examples Fetched', props<{ commandExamples: CommandExample[] }>());
  static commandsComponentExecuteClicked = createAction(source + 'Commands Component Execute Clicked', props<{ command: ExecutableCommand }>());
  static controlStateFetched = createAction(source + 'Control State Fetched', props<{ controlState: ControlState }>());
  static controlCommandExecutionFailed = createAction(source + 'Control Command Execution Failed');
  static controlCommandExecutionSucceeded = createAction(source + 'Control Command Execution Succeeded');
  static recentRunDetailsInitialized = createAction(source + 'Recent Run Details Initialized');
  static recentRunDetailsDestroyed = createAction(source + 'Recent Run Details Destroyed');
  static recentRunFetched = createAction(source + 'Recent Run Fetched', props<{ recentRun: RecentRun }>());
  static recentRunFailedToLoad = createAction(source + 'Recent Run Failed To Load', props<{ error: ApiError }>());
  static recentRunDownloadCsvButtonClicked = createAction(source + 'Recent Run Download Csv Button Clicked', props<{ recentRunId: string }>());
  static recentRunDownloadArchiveButtonClicked = createAction(source + 'Recent Run Download Archive Button Clicked',
    props<{ recentRunId: string }>());
  static controlStateUpdatedOnBackend = createAction(source + 'Control State Updated On Backend', props<{ unitId: string }>());
  static toggleAllProcessValues = createAction(source + 'All Process Values Toggled', props<{ allProcessValues: boolean }>());
  static processUnitNavigatedFrom = createAction(source + 'Process Unit Navigated From', props<{ oldUnitId?: string, newUnitId?: string }>());
  static otherActiveUsersFetched = createAction(source + 'Other Active Users Fetched', props<{ otherActiveUsers: ActiveUser[] }>());
  static activeUsersUpdatedOnBackend = createAction(source + 'Active Users Updated On Backend', props<{ unitId: string }>());
}
