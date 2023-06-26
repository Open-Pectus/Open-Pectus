import { createAction, props } from '@ngrx/store';
import { ProcessValue, ProcessValueCommand } from '../../../api';

const source = '[Process Values] ';

export class ProcessValuesActions {
  static processValuesComponentInitialized = createAction(source + 'Process Values Component Initialized');
  static processValuesComponentDestroyed = createAction(source + 'Process Values Component Destroyed');
  static processValueEdited = createAction(source + 'Process Value Edited', props<{ processValue: ProcessValue }>());
  static processValueCommandClicked = createAction(source + 'Process Value Command Clicked',
    props<{ command: ProcessValueCommand, processValueName: string }>());
}
