import { createAction, props } from '@ngrx/store';
import { RecentRun } from '../../api/models/RecentRun';

export class DashboardActions {
  static source = 'Dashboard';
  static recentRunsFilterChanged = createAction(this.source + 'Recent Runs Filter Changed', props<{ filter: string }>());
  static recentRunsInitialized = createAction(this.source + 'Recent Runs Initialized');
  static recentRunsLoaded = createAction(this.source + 'Recent Runs Loaded', props<{ recentRuns: RecentRun[] }>());
}


