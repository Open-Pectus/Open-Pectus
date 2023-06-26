import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit, QueryList, ViewChildren } from '@angular/core';
import { Store } from '@ngrx/store';
import { produce } from 'immer';
import { BehaviorSubject, combineLatest, map } from 'rxjs';
import { RunLog } from '../../api';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { RunLogLineComponent } from './run-log-line.component';

@Component({
  selector: 'app-run-log',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Run Log'" [heightResizable]="true" [contentHeight]="400" (collapseStateChanged)="collapsed = $event">
      <label buttons class="relative">
        <input type="text" placeholder="Filter Run Log" size="20"
               class="border border-slate-200 placeholder:text-slate-400 text-white bg-transparent outline-none rounded p-1 h-8"
               #filterInput (input)="filterText.next(filterInput.value)">
        <button *ngIf="filterInput.value.length !== 0" class="p-2 codicon codicon-chrome-close absolute right-0"
                (click)="filterInput.value = ''"></button>
      </label>
      <label buttons class="flex items-center gap-1 cursor-pointer border rounded px-1 border-slate-200 h-8">
        In progress only
        <input type="checkbox" (input)="onlyRunning.next(onlyRunningCheckbox.checked)" #onlyRunningCheckbox
               [class.codicon-pass]="onlyRunningCheckbox.checked" [class.codicon-circle-large]="!onlyRunningCheckbox.checked"
               class="w-5 !text-xl appearance-none font-bold opacity-25 text-white checked:opacity-100 codicon cursor-pointer">
      </label>
      <div content *ngIf="!collapsed" class="h-full overflow-y-auto">
        <app-run-log-header [gridFormat]="gridFormat" (expandAll)="expandAll()" (collapseAll)="collapseAll()"></app-run-log-header>
        <app-run-log-line *ngFor="let runLogLine of (runLog | ngrxPush)?.lines; let index = index" [runLogLine]="runLogLine" [rowIndex]="index"
                          [gridFormat]="gridFormat" [dateFormat]="dateFormat"></app-run-log-line>
        <p class="text-center p-2 font-semibold" *ngIf="(runLog | ngrxPush)?.lines?.length === 0">
          No Run Log available or all have been filtered.
        </p>
      </div>
    </app-collapsible-element>
  `,
})
export class RunLogComponent implements OnInit {
  @ViewChildren(RunLogLineComponent) runLogLines?: QueryList<RunLogLineComponent>;
  protected collapsed = false;
  protected onlyRunning = new BehaviorSubject<boolean>(false);
  protected filterText = new BehaviorSubject<string>('');
  protected readonly gridFormat = 'auto / 15ch 15ch 1fr auto auto';
  protected readonly dateFormat = 'MM-dd HH:mm:ss';
  protected runLog = combineLatest([
    this.store.select(DetailsSelectors.runLog),
    this.onlyRunning,
    this.filterText,
  ]).pipe<RunLog>(map(([runLog, checked, filterText]) => produce(runLog, draft => {
    if(checked) draft.lines = draft.lines.filter(line => line.end === undefined);
    if(filterText !== '') {
      draft.lines = draft.lines.filter(line => {
        return this.datePipe.transform(line.end, this.dateFormat)?.includes(filterText) ||
               this.datePipe.transform(line.start, this.dateFormat)?.includes(filterText) ||
               line.command.command.toLowerCase().includes(filterText.toLowerCase());
      });
    }
    draft.lines.sort((a, b) => new Date(a.start).valueOf() - new Date(b.start).valueOf());
  })));

  constructor(private store: Store,
              private datePipe: DatePipe) {}

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
