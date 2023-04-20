import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { DashboardActions } from '../ngrx/dashboard.actions';

@Component({
  selector: 'app-dashboard',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex justify-center">
      <div class="flex flex-col max-w-5xl mx-8">
        <div class="text-xl font-semibold my-6 text-gray-500">Process Units:</div>
        <app-dashboard-process-units class="mb-6"></app-dashboard-process-units>
        <div class="text-xl font-semibold my-6 text-gray-500">Recent Batch Jobs:</div>
        <app-recent-batch-jobs></app-recent-batch-jobs>
      </div>
    </div>
  `,
})
export class DashboardComponent implements OnInit {
  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DashboardActions.pageInitialized());
  }

}
