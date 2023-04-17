import { createActionGroup, props } from '@ngrx/store';

export const AppActions = createActionGroup({
  source: 'App',
  events: {
    'A Test Action': props<{ aString: string }>()
  }
});
