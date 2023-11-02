import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { BatchJob } from '../../api';
import { detailsUrlPart } from '../../app-routing.module';
import { DetailsRoutingUrlParts } from '../../details/details-routing-url-parts';
import { DefaultTableSort, TableColumn, TableSortDirection } from '../../shared/table.component';
import { DashboardActions } from '../ngrx/dashboard.actions';
import { DashboardSelectors } from '../ngrx/dashboard.selectors';


@Component({
  selector: 'app-recent-batch-jobs',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-table class="w-full h-96" [columns]="columns" [data]="recentBatchJobs | ngrxPush" (rowClicked)="navigateToBatchJob($event)"
               [defaultSort]="defaultSort" [filter]="recenterBatchJobFilter | ngrxPush"></app-table>
    <div class="text-center p-2" *ngIf="(recentBatchJobs | ngrxPush)?.length === 0">No recent batch jobs available</div>
  `,
})
export class RecentBatchJobsComponent implements OnInit {
  protected readonly recenterBatchJobFilter = this.store.select(DashboardSelectors.recentBatchJobFilter);
  protected readonly recentBatchJobs = this.store.select(DashboardSelectors.recentBatchJobs);
  protected readonly defaultSort: DefaultTableSort<BatchJob> = {columnKey: 'completed_date', direction: TableSortDirection.Descending};
  protected readonly columns: TableColumn<BatchJob>[] = [
    {
      header: 'Unit',
      key: 'unit_name',
    },
    {
      header: 'Started',
      key: 'started_date',
      isDate: true,
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


  constructor(private router: Router, private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DashboardActions.recentBatchJobsInitialized());
  }

  navigateToBatchJob(batchJob: BatchJob) {
    this.router.navigate([detailsUrlPart, DetailsRoutingUrlParts.batchJobUrlPart, batchJob.id]).then();
  }
}
