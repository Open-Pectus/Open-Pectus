import { createActionGroup, emptyProps, props } from '@ngrx/store';

export const DetailsActions = createActionGroup({
  source: 'Details',
  events: {
    'Method Editor Model Changed': props<{ model: string }>(),
    'Method Editor Model Save Requested': emptyProps(),
    'Method Editor Model Saved': emptyProps(),
  },
});
