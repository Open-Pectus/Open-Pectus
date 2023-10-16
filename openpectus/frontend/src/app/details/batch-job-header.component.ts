import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-batch-job-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ng-container *ngrxLet="batchJob as batchJob">
      <div class="text-slate-700 mb-1">
        <div class="text-xs flex gap-4 mb-2">
          <span>Started at: <b class="whitespace-nowrap">{{batchJob?.started_date | date}}</b></span>
          <span>Finished at: <b class="whitespace-nowrap">{{batchJob?.completed_date | date}}</b></span>
          <span>Contributions by: <b>{{batchJob?.contributors?.join(', ')}}</b></span>
        </div>
        <h1 class="text-4xl lg:text-5xl font-bold">{{batchJob?.unit_name}}</h1>
      </div>
    </ng-container>
  `,
})
export class BatchJobHeaderComponent {
  protected batchJob = this.store.select(DetailsSelectors.batchJob);

  constructor(private store: Store) {}
}
