import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { RecentRun } from '../../api';
import { detailsUrlPart } from '../../app.routes';
import { DetailsRoutingUrlParts } from '../../details/details-routing-url-parts';
import { DefaultTableSort, TableColumn, TableComponent, TableSortDirection } from '../../shared/table.component';
import { DashboardActions } from '../ngrx/dashboard.actions';
import { DashboardSelectors } from '../ngrx/dashboard.selectors';


@Component({
  selector: 'app-recent-runs',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    TableComponent,
    NgIf,
    PushPipe,
  ],
  template: `
    <app-table class="w-full h-96" [columns]="columns" [data]="recentRuns | ngrxPush" (rowClicked)="navigateToRecentRun($event)"
               [defaultSort]="defaultSort" [filter]="recentRunsFilter | ngrxPush"></app-table>
    <div class="text-center p-2" *ngIf="(recentRuns | ngrxPush)?.length === 0">No recent runs available</div>
  `,
})
export class RecentRunsComponent implements OnInit {
  protected readonly recentRunsFilter = this.store.select(DashboardSelectors.recentRunsFilter);
  protected readonly recentRuns = this.store.select(DashboardSelectors.recentRuns);
  protected readonly defaultSort: DefaultTableSort<RecentRun> = {columnKey: 'completed_date', direction: TableSortDirection.Descending};
  protected readonly columns: TableColumn<RecentRun>[] = [
    {
      header: 'Unit',
      key: 'engine_id',
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
    this.store.dispatch(DashboardActions.recentRunsInitialized());
  }

  navigateToRecentRun(recentRun: RecentRun) {
    this.router.navigate([detailsUrlPart, DetailsRoutingUrlParts.recentRunUrlPart, recentRun.run_id]).then();
  }
}
