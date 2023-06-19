import { createActionGroup, emptyProps, props } from '@ngrx/store';
import { CommandExample, ExecutableCommand, ProcessDiagram, ProcessUnit, ProcessValue, ProcessValueCommand, RunLog } from '../../api';

export const DetailsActions = createActionGroup({
  source: 'Details',
  events: {
    'Method Editor Initialized': props<{ model: string }>(),
    'Method Editor Model Changed': props<{ model: string }>(),
    'Method Editor Model Save Requested': emptyProps(),
    'Method Editor Model Saved': emptyProps(),

    'Process Values Initialized': emptyProps(),
    'Process Values Destroyed': emptyProps(),
    'Process Values Fetched': props<{ processValues: ProcessValue[] }>(),
    'Process Values Failed to load': emptyProps(),
    'Process Value Edited': props<{ processValue: ProcessValue }>(),
    'Process Value Command Clicked': props<{ command: ProcessValueCommand, processValueName: string }>(),

    'Process Unit Loaded': props<{ processUnit: ProcessUnit }>(),
    'Process Unit Command Button Clicked': props<{ command: ExecutableCommand }>(),

    'Process Diagram Initialized': emptyProps(),
    'Process Diagram Fetched': props<{ processDiagram: ProcessDiagram }>(),

    'Commands Component Initialized': emptyProps(),
    'Command Examples Fetched': props<{ commandExamples: CommandExample[] }>(),
    'Commands Component Execute Clicked': props<{ command: ExecutableCommand }>(),

    'Run Log Component Initialized': emptyProps(),
    'Run Log Fetched': props<{ runLog: RunLog }>(),
  },
});
