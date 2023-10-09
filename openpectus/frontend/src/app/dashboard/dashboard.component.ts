import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { DashboardActions } from './ngrx/dashboard.actions';

@Component({
  selector: 'app-dashboard',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex justify-center">
      <div class="flex flex-col max-w-5xl mx-4 md:mx-8">
        <div class="text-xl font-semibold my-6 text-gray-500">Process Units:</div>
        <app-dashboard-process-units class="mb-6"></app-dashboard-process-units>
        <div class="flex justify-between items-center">
          <div class="text-xl font-semibold my-6 text-gray-500">Recent Batch Jobs:</div>
          <input type="text" placeholder="Filter Recent Batch Jobs" size="25" class="border-b-2 border-slate-400 p-1" #filterInput
                 (input)="filterChange(filterInput.value)">
        </div>
        <app-recent-batch-jobs></app-recent-batch-jobs>
      </div>
    </div>
  `,
})
export class DashboardComponent {
  constructor(private store: Store) {}

  filterChange(filter: string) {
    this.store.dispatch(DashboardActions.recentBatchJobFilterChanged({filter}));
  }
}
