import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { selectRouteParam } from '../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from './details-routing-url-parts';
import { ErrorLogComponent } from './error-log/error-log.component';
import { MethodEditorComponent } from './method-editor/method-editor.component';
import { MissingRolesComponent } from './missing-roles.component';
import { DetailsActions } from './ngrx/details.actions';
import { ProcessPlotContainerComponent } from './process-plot/process-plot-container.component';
import { RecentRunHeaderComponent } from './recent-run-header.component';
import { RunLogComponent } from './run-log/run-log.component';

@Component({
    selector: 'app-recent-run-details',
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [
        LetDirective,
        RecentRunHeaderComponent,
        ProcessPlotContainerComponent,
        MethodEditorComponent,
        RunLogComponent,
        ErrorLogComponent,
        MissingRolesComponent,
    ],
    template: `
    <app-missing-roles>
      <div class="flex justify-center">
        <div class="grid grid-cols-1 2xl:grid-cols-2 w-full lg:px-6 lg:py-6 gap-4 lg:gap-6" *ngrxLet="recentRunId as recentRunId">
          <app-recent-run-header class="2xl:col-span-2 mx-2 mt-3 lg:m-0"></app-recent-run-header>
          <app-process-plot-container [recentRunId]="recentRunId" class="2xl:col-span-2"></app-process-plot-container>
          <app-method-editor [recentRunId]="recentRunId"></app-method-editor>
          <app-run-log [recentRunId]="recentRunId"></app-run-log>
          <app-error-log [recentRunId]="recentRunId" class="2xl:col-span-2"></app-error-log>
        </div>
      </div>
    </app-missing-roles>
  `
})
export class RecentRunDetailsComponent implements OnInit, OnDestroy {
  protected recentRunId = this.store.select(selectRouteParam(DetailsRoutingUrlParts.recentRunIdParamName));

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.recentRunDetailsInitialized());
  }

  ngOnDestroy() {
    this.store.dispatch(DetailsActions.recentRunDetailsDestroyed());
  }
}
