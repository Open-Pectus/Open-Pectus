import { createAction, props } from '@ngrx/store';
import { ProcessValueCommand } from '../../../api/models/ProcessValueCommand';

const source = '[Process Values] ';

export class ProcessValuesActions {
  static processValuesComponentInitialized = createAction(source + 'Process Values Component Initialized');
  static processValuesComponentDestroyed = createAction(source + 'Process Values Component Destroyed');
  static processValueCommandClicked = createAction(source + 'Process Value Command Clicked',
    props<{ command: ProcessValueCommand, processValueName: string }>());
}
