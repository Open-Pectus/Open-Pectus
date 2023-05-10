import { createActionGroup, emptyProps, props } from '@ngrx/store';
import { ProcessUnit } from '../api';

export const AppActions = createActionGroup({
  source: 'App',
  events: {
    'Page initialized': emptyProps(),
    'Process Units loaded': props<{ processUnits: ProcessUnit[] }>(),
  },
});
