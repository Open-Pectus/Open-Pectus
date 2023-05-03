import { createActionGroup, emptyProps, props } from '@ngrx/store';
import { ProcessValue } from '../api';

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
  },
});
