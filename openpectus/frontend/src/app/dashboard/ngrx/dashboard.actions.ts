import { createActionGroup, emptyProps, props } from '@ngrx/store';
import { BatchJob } from '../../api';

export const DashboardActions = createActionGroup({
  source: 'Dashboard',
  events: {
    'Recent Batch Job Filter Changed': props<{ filter: string }>(),
    'Recent Batch Jobs Initialized': emptyProps(),
    'Recent Batch Jobs Loaded': props<{ recentBatchJobs: BatchJob[] }>(),
  },
});
