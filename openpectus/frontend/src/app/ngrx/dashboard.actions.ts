import { createActionGroup, emptyProps, props } from '@ngrx/store';
import { BatchJob, ProcessUnit } from '../api';

export const DashboardActions = createActionGroup({
  source: 'Dashboard',
  events: {
    'Page initialized': emptyProps(),
    'Process Units loaded': props<{ processUnits: ProcessUnit[] }>(),
    'Recent Batch Job Filter Changed': props<{ filter: string }>(),
    'Recent Batch Jobs Initialized': emptyProps(),
    'Recent Batch Jobs Loaded': props<{ recentBatchJobs: BatchJob[] }>(),
  },
});
