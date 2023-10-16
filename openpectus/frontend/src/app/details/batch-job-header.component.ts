import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { BatchJob } from '../api';
import { DetailsActions } from './ngrx/details.actions';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-batch-job-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ng-container *ngrxLet="batchJob as batchJob">
      <div class="text-slate-700 mb-1 relative">
        <div class="text-xs flex gap-4 mb-2">
          <span>Started at: <b class="whitespace-nowrap">{{batchJob?.started_date | date}}</b></span>
          <span>Finished at: <b class="whitespace-nowrap">{{batchJob?.completed_date | date}}</b></span>
          <span>Contributions by: <b>{{batchJob?.contributors?.join(', ')}}</b></span>
        </div>
        <h1 class="text-4xl lg:text-5xl font-bold">{{batchJob?.unit_name}}</h1>

        <button class="absolute top-0 right-0 px-3 py-1.5 rounded-md bg-sky-900 text-white flex items-center"
                (click)="downloadCsv(batchJob)">
          <i class="codicon codicon-desktop-download !text-xl mr-2.5"></i>
          Data CSV-file
        </button>
      </div>
    </ng-container>
  `,
})
export class BatchJobHeaderComponent {
  protected batchJob = this.store.select(DetailsSelectors.batchJob);

  constructor(private store: Store) {}

  downloadCsv(batchJob?: BatchJob) {
    if(batchJob === undefined) return;
    this.store.dispatch(DetailsActions.batchJobDownloadCsvButtonClicked({url: batchJob.csv_url}));
  }
}
