import { createAction, props } from '@ngrx/store';
import { ExecutableCommand } from '../../api/models/ExecutableCommand';

const source = '[Details] ';

export class DetailsActions {
  static unitDetailsInitialized = createAction(source + 'Unit Details Initialized', props<{ unitId: string }>());
  static unitDetailsDestroyed = createAction(source + 'Unit Details Destroyed');
  static processUnitCommandButtonClicked = createAction(source + 'Process Unit Command Button Clicked',
    props<{ command: string }>());
  static commandsComponentExecuteClicked = createAction(source + 'Commands Component Execute Clicked', props<{ command: ExecutableCommand }>());
  static recentRunDownloadCsvButtonClicked = createAction(source + 'Recent Run Download Csv Button Clicked', props<{ recentRunId: string }>());
  static toggleAllProcessValues = createAction(source + 'All Process Values Toggled', props<{ allProcessValues: boolean }>());
}
