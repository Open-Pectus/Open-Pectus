import { createAction, props } from '@ngrx/store';
import { CommandExample } from '../../api/models/CommandExample';
import { ControlState } from '../../api/models/ControlState';
import { ExecutableCommand } from '../../api/models/ExecutableCommand';
import { ProcessValue } from '../../api/models/ProcessValue';
import { RecentRun } from '../../api/models/RecentRun';

const source = '[Details] ';

export class DetailsActions {
  static unitDetailsInitialized = createAction(source + 'Unit Details Initialized', props<{ unitId: string }>());
  static unitDetailsDestroyed = createAction(source + 'Unit Details Destroyed');
  static processValuesFetched = createAction(source + 'Process Values Fetched', props<{ processValues: ProcessValue[] }>());
  static processUnitCommandButtonClicked = createAction(source + 'Process Unit Command Button Clicked',
    props<{ command: string }>());
  static commandsComponentInitialized = createAction(source + 'Commands Component Initialized');
  static commandExamplesFetched = createAction(source + 'Command Examples Fetched', props<{ commandExamples: CommandExample[] }>());
  static commandsComponentExecuteClicked = createAction(source + 'Commands Component Execute Clicked', props<{ command: ExecutableCommand }>());
  static controlStateFetched = createAction(source + 'Control State Fetched', props<{ controlState: ControlState }>());
  static recentRunDetailsInitialized = createAction(source + 'Recent Run Details Initialized');
  static recentRunDetailsDestroyed = createAction(source + 'Recent Run Details Destroyed');
  static recentRunFetched = createAction(source + 'Recent Run Fetched', props<{ recentRun: RecentRun }>());
  static recentRunDownloadCsvButtonClicked = createAction(source + 'Recent Run Download Csv Button Clicked', props<{ recentRunId: string }>());
  static controlStateUpdatedOnBackend = createAction(source + 'Control State Updated On Backend', props<{ unitId: string }>());
  static toggleAllProcessValues = createAction(source + 'All Process Values Toggled', props<{ allProcessValues: boolean }>());
}
