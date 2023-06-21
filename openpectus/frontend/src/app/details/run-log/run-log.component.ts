import { ChangeDetectionStrategy, Component, OnInit, QueryList, ViewChildren } from '@angular/core';
import { Store } from '@ngrx/store';
import { produce } from 'immer';
import { map } from 'rxjs';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { RunLogLineComponent } from './run-log-line.component';

@Component({
  selector: 'app-run-log',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Run Log'" [heightResizable]="true" [contentHeight]="400">
      <div content *ngrxLet="runLog as runLog" class="h-full">
        <div class="grid bg-gray-700 text-white gap-2 px-3 py-2" [style.grid]="gridFormat">
          <b>Start</b>
          <b>End</b>
          <b>Command</b>
          <button class="bg-gray-500 rounded px-2 flex items-center" (click)="expandAll()">
            <div class="codicon codicon-unfold mr-1"></div>
            Expand all
          </button>
          <button class="bg-gray-500 rounded px-2 flex items-center" (click)="collapseAll()">
            <div class="codicon codicon-fold mr-1"></div>
            Collapse all
          </button>
        </div>
        <app-run-log-line *ngFor="let runLogLine of runLog.lines; let index = index" [runLogLine]="runLogLine" [rowIndex]="index"
                          [gridFormat]="gridFormat"></app-run-log-line>
        <p class="text-center p-2 font-semibold" *ngIf="runLog.lines.length === 0">
          No Run Log available.
        </p>
      </div>
    </app-collapsible-element>
  `,
})
export class RunLogComponent implements OnInit {
  runLog = this.store.select(DetailsSelectors.runLog).pipe(map(runLog => produce(runLog, draft => {
      draft.lines.sort((a, b) => new Date(a.start).valueOf() - new Date(b.start).valueOf());
    }),
  ));
  gridFormat = 'auto / 15ch 15ch 1fr auto auto';
  @ViewChildren(RunLogLineComponent) runLogLines?: QueryList<RunLogLineComponent>;

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.runLogComponentInitialized());
  }

  expandAll() {
    this.runLogLines?.forEach(runLogLineComponent => runLogLineComponent.collapsed = false);
  }

  collapseAll() {
    this.runLogLines?.forEach(runLogLineComponent => runLogLineComponent.collapsed = true);
  }
}
