import { createActionGroup, emptyProps, props } from '@ngrx/store';
import { ProcessUnit } from '../api';

export const DashboardActions = createActionGroup({
  source: 'Dashboard',
  events: {
    'Page initialized': emptyProps(),
    'Process Units loaded': props<{ processUnits: ProcessUnit[] }>(),
  },
});
