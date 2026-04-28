import { ChangeDetectionStrategy, Component, inject, input, OnDestroy, OnInit, QueryList, ViewChildren } from '@angular/core';
import { Store } from '@ngrx/store';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { RunLogActions } from './ngrx/run-log.actions';
import { RunLogSelectors } from './ngrx/run-log.selectors';
import { RunLogFiltersComponent } from './run-log-filters.component';
import { RunLogHeaderComponent } from './run-log-header.component';
import { RunLogLineComponent } from './run-log-line/run-log-line.component';

@Component({
  selector: 'app-run-log',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CollapsibleElementComponent,
    RunLogFiltersComponent,
    RunLogHeaderComponent,
    RunLogLineComponent,
  ],
  template: `
    <app-collapsible-element [name]="'Run Log'" [heightResizable]="true" [initialContentHeight]="400"
                             (collapseStateChanged)="collapsed = $event"
                             [codiconName]="'codicon-tasklist'">
      <app-run-log-filters buttons [showRunningFilter]="unitId() !== undefined"></app-run-log-filters>
      @if (!collapsed) {
        <div content class="h-full overflow-auto">
          <div class="min-w-fit">
            <app-run-log-header [gridFormat]="gridFormat" (expandAll)="expandAll()" (collapseAll)="collapseAll()"></app-run-log-header>
            @for (runLogLine of runLog().lines; track runLogLine.id; let index = $index) {
              <app-run-log-line [runLogLine]="runLogLine"
                                [rowIndex]="index"
                                [gridFormat]="gridFormat"></app-run-log-line>
            }
            @if (runLog().lines.length === 0) {
              <p class="text-center p-2 font-semibold">
                No Run Log available or all have been filtered.
              </p>
            }
          </div>
        </div>
      }
    </app-collapsible-element>
  `
})
export class RunLogComponent implements OnInit, OnDestroy {
  readonly unitId = input<string>();
  readonly recentRunId = input<string>();
  @ViewChildren(RunLogLineComponent) runLogLines?: QueryList<RunLogLineComponent>;
  protected collapsed = false;
  protected readonly gridFormat = 'auto / 15ch 15ch 1fr auto auto';
  private store = inject(Store);
  protected runLog = this.store.selectSignal(RunLogSelectors.runLog);

  ngOnInit() {
    const unitId = this.unitId();
    if(unitId !== undefined) this.store.dispatch(RunLogActions.runLogComponentInitializedForUnit({unitId: unitId}));
    const recentRunId = this.recentRunId();
    if(recentRunId !== undefined) {
      this.store.dispatch(RunLogActions.runLogComponentInitializedForRecentRun({recentRunId: recentRunId}));
    }
  }

  ngOnDestroy() {
    this.store.dispatch(RunLogActions.runLogComponentDestroyed());
  }

  expandAll() {
    this.store.dispatch(RunLogActions.expandAll());
  }

  collapseAll() {
    this.store.dispatch(RunLogActions.collapseAll());
  }
}
