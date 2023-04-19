import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { DashboardActions } from '../ngrx/dashboard.actions';

@Component({
  selector: 'app-dashboard',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col max-w-5xl m-auto">
      <!-- recent batchjobs -->
      <app-dashboard-process-units></app-dashboard-process-units>
    </div>
  `,
})
export class DashboardComponent implements OnInit {
  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DashboardActions.pageInitialized());
  }

}
