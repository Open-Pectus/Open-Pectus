import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-batch-job-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ng-container *ngrxLet="batchJob as batchJob">
      <div class="text-slate-700 mb-1">
        <div class="text-sm">
          <span>Finished at: <b>{{batchJob?.completed_date | date:'MM-dd HH:mm:ss'}}</b></span>
          <span class="ml-4">Contributions by: <b>{{batchJob?.contributors?.join(', ')}}</b></span>
        </div>
        <h1 class="text-4xl font-bold">{{batchJob?.unit_name}}</h1>
      </div>
    </ng-container>
  `,
})
export class BatchJobHeaderComponent {
  protected batchJob = this.store.select(DetailsSelectors.batchJob);

  constructor(private store: Store) {}
}
