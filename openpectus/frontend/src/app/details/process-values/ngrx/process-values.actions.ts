import { createAction, props } from '@ngrx/store';
import { ProcessValue, ProcessValueCommand } from '../../../api';

const source = '[Process Values] ';

export class ProcessValuesActions {
  static processValuesInitialized = createAction(source + 'Process Values Initialized');
  static processValuesDestroyed = createAction(source + 'Process Values Destroyed');
  static processValueEdited = createAction(source + 'Process Value Edited', props<{ processValue: ProcessValue }>());
  static processValueCommandClicked = createAction(source + 'Process Value Command Clicked',
    props<{ command: ProcessValueCommand, processValueName: string }>());
}
