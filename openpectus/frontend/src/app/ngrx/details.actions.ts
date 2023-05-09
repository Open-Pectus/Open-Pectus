import { createActionGroup, emptyProps, props } from '@ngrx/store';
import { ProcessUnit, ProcessValue, ProcessValueCommand } from '../api';

export const DetailsActions = createActionGroup({
  source: 'Details',
  events: {
    'Method Editor Initialized': props<{ model: string }>(),
    'Method Editor Model Changed': props<{ model: string }>(),
    'Method Editor Model Save Requested': emptyProps(),
    'Method Editor Model Saved': emptyProps(),
    'Process Values Initialized': emptyProps(),
    'Process Values Loaded': props<{ processValues: ProcessValue[] }>(),
    'Process Values Failed to load': emptyProps(),
    'Process Value Command Clicked': props<{ command: ProcessValueCommand, processValueName: string }>(),
    'Details Page Initialized': emptyProps(),
    'Process Unit Loaded': props<{ processUnit: ProcessUnit }>(),
  },
});
