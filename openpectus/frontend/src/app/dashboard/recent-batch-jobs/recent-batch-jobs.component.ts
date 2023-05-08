import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router } from '@angular/router';
import { sub } from 'date-fns';
import { BatchJob } from '../../api';
import { detailsUrlPart } from '../../app-routing.module';
import { batchJobUrlPart } from '../../details/details-routing.module';
import { TableColumn } from '../../shared/table.component';


const randomDate1 = sub(new Date(), {seconds: Math.random() * 1000000}).toISOString();
const randomDate3 = sub(new Date(), {seconds: Math.random() * 1000000}).toISOString();
const tenMinutesAgo = sub(new Date(), {seconds: Math.random() * 1000000}).toISOString();

@Component({
  selector: 'app-recent-batch-jobs',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-table class="w-full h-96" [columns]="columns" [data]="data" (rowClicked)="navigateToBatchJob($event)"></app-table>
  `,
})
export class RecentBatchJobsComponent {
  protected readonly columns: TableColumn<BatchJob>[] = [
    {
      header: 'Unit',
      key: 'unit_name',
    },
    {
      header: 'Completed',
      key: 'completed_date',
      isDate: true,
    },
    {
      header: 'Contributors',
      key: 'contributors',
    },
  ];

  protected readonly data: BatchJob[] = [
    {id: 1, unit_id: 1, unit_name: 'Some Name 1', completed_date: new Date().toISOString(), contributors: ['Eskild']},
    {id: 2, unit_id: 2, unit_name: 'Some Name 2', completed_date: randomDate1, contributors: ['Eskild', 'Morten']},
    {id: 3, unit_id: 3, unit_name: 'Some Name 3', completed_date: randomDate3, contributors: ['Eskild']},
    {id: 4, unit_id: 4, unit_name: 'Some Name 4', completed_date: tenMinutesAgo, contributors: ['Eskild']},
  ];

  constructor(private router: Router) {}

  navigateToBatchJob(batchJob: BatchJob) {
    this.router.navigate([detailsUrlPart, batchJobUrlPart, batchJob.id]).then();
  }
}
