import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { selectRouteParam } from '../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from './details-routing-url-parts';
import { DetailsActions } from './ngrx/details.actions';

@Component({
  selector: 'app-batch-job-details',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex justify-center">
      <div class="grid grid-cols-1 2xl:grid-cols-2 w-full lg:px-6 lg:py-8 gap-4 lg:gap-8">
        <app-method-editor [batchJobId]="batchJobId | ngrxPush"></app-method-editor>
        <app-run-log [batchJobId]="batchJobId | ngrxPush"></app-run-log>
        <app-process-plot-container class="2xl:col-span-2"></app-process-plot-container>
      </div>
    </div>
  `,
})
export class BatchJobDetailsComponent implements OnInit, OnDestroy {
  protected batchJobId = this.store.select(selectRouteParam(DetailsRoutingUrlParts.batchJobIdParamName));

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.batchJobDetailsInitialized());
  }

  ngOnDestroy() {
    this.store.dispatch(DetailsActions.batchJobDetailsDestroyed());
  }
}
