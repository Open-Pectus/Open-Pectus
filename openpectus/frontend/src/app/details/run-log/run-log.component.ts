import { NgFor, NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input, OnDestroy, OnInit, QueryList, ViewChildren } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { RunLogLine } from '../../api';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { RunLogActions } from './ngrx/run-log.actions';
import { RunLogSelectors } from './ngrx/run-log.selectors';
import { RunLogFiltersComponent } from './run-log-filters.component';
import { RunLogHeaderComponent } from './run-log-header.component';
import { RunLogLineComponent } from './run-log-line/run-log-line.component';

@Component({
  selector: 'app-run-log',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    CollapsibleElementComponent,
    RunLogFiltersComponent,
    NgIf,
    RunLogHeaderComponent,
    NgFor,
    RunLogLineComponent,
    PushPipe,
  ],
  template: `
    <app-collapsible-element [name]="'Run Log'" [heightResizable]="true" [contentHeight]="400" (collapseStateChanged)="collapsed = $event"
                             [codiconName]="'codicon-tasklist'">
      <app-run-log-filters buttons [showRunningFilter]="(unitId | ngrxPush) !== undefined"></app-run-log-filters>
      <div content *ngIf="!collapsed" class="h-full overflow-auto">
        <div class="min-w-fit">
          <app-run-log-header [gridFormat]="gridFormat" (expandAll)="expandAll()" (collapseAll)="collapseAll()"></app-run-log-header>
          <app-run-log-line *ngFor="let runLogLine of (runLog | ngrxPush)?.lines; let index = index; trackBy: trackBy" [runLogLine]="runLogLine"
                            [rowIndex]="index"
                            [gridFormat]="gridFormat"></app-run-log-line>
          <p class="text-center p-2 font-semibold" *ngIf="(runLog | ngrxPush)?.lines?.length === 0">
            No Run Log available or all have been filtered.
          </p>
        </div>
      </div>
    </app-collapsible-element>
  `,
})
export class RunLogComponent implements OnInit, OnDestroy {
  @Input() unitId?: string;
  @Input() batchJobId?: string;
  @ViewChildren(RunLogLineComponent) runLogLines?: QueryList<RunLogLineComponent>;
  protected runLog = this.store.select(RunLogSelectors.runLog);
  protected collapsed = false;
  protected readonly gridFormat = 'auto / 15ch 15ch 1fr auto auto';

  constructor(private store: Store) {}

  trackBy(_: number, runLogLine: RunLogLine) {
    return runLogLine.id;
  }

  ngOnInit() {
    if(this.unitId !== undefined) this.store.dispatch(RunLogActions.runLogComponentInitializedForUnit({unitId: this.unitId}));
    if(this.batchJobId !== undefined) this.store.dispatch(RunLogActions.runLogComponentInitializedForBatchJob({batchJobId: this.batchJobId}));
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
