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
      <div class="grid grid-cols-1 2xl:grid-cols-2 w-full lg:px-6 lg:py-8 gap-4 lg:gap-8" *ngrxLet="batchJobId as batchJobId">
        <app-batch-job-header class="2xl:col-span-2 mx-2 mt-3 lg:m-0"></app-batch-job-header>
        <app-process-plot-container [batchJobId]="batchJobId" class="2xl:col-span-2"></app-process-plot-container>
        <app-method-editor [batchJobId]="batchJobId"></app-method-editor>
        <app-run-log [batchJobId]="batchJobId"></app-run-log>
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
