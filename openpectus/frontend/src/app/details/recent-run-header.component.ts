import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { DetailsQueriesService } from './details-queries.service';
import { DetailsActions } from './ngrx/details.actions';

@Component({
  selector: 'app-recent-run-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [LetDirective, DatePipe],
  template: `
    <ng-container *ngrxLet="recentRunQuery.data() as recentRun">
      <div class="text-slate-700 mb-1 relative">
        <div class="text-xs flex gap-4 mb-2">
          <span>Started at: <b class="whitespace-nowrap">{{ recentRun?.started_date | date }}</b></span>
          <span>Finished at: <b class="whitespace-nowrap">{{ recentRun?.completed_date | date }}</b></span>
          <span>Contributions by: <b>{{ recentRun?.contributors?.join(', ') }}</b></span>
        </div>
        <h1 class="text-4xl lg:text-5xl font-bold">{{ recentRun?.engine_id }}</h1>

        <button class="absolute top-0 right-0 px-3 py-1.5 rounded-md bg-sky-900 text-white flex items-center"
                (click)="downloadCsv(recentRun?.run_id)">
          <i class="codicon codicon-desktop-download !text-xl mr-2.5"></i>
          Data CSV-file
        </button>
      </div>
    </ng-container>
  `,
})
export class RecentRunHeaderComponent {
  protected recentRunQuery = this.detailsQueriesService.injectRecentRunQuery();

  constructor(private store: Store,
              private detailsQueriesService: DetailsQueriesService) {}

  downloadCsv(recentRunId?: string) {
    if(recentRunId === undefined) return;
    this.store.dispatch(DetailsActions.recentRunDownloadCsvButtonClicked({recentRunId}));
  }
}
