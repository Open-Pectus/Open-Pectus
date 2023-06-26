import { createActionGroup, emptyProps, props } from '@ngrx/store';
import { CommandExample, ExecutableCommand, ProcessDiagram, ProcessUnit, ProcessValue } from '../../api';

export const DetailsActions = createActionGroup({
  source: 'Details',
  events: {
    'Unit Details Initialized': emptyProps(),
    'Unit Details Destroyed': emptyProps(),
    'Process Values Fetched': props<{ processValues: ProcessValue[] }>(),
    'Process Values Failed to load': emptyProps(),

    'Process Unit Loaded': props<{ processUnit: ProcessUnit }>(),
    'Process Unit Command Button Clicked': props<{ command: ExecutableCommand }>(),

    'Process Diagram Initialized': emptyProps(),
    'Process Diagram Fetched': props<{ processDiagram: ProcessDiagram }>(),

    'Commands Component Initialized': emptyProps(),
    'Command Examples Fetched': props<{ commandExamples: CommandExample[] }>(),
    'Commands Component Execute Clicked': props<{ command: ExecutableCommand }>(),
  },
});
