import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, ElementRef, OnInit, QueryList, ViewChild, ViewChildren } from '@angular/core';
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
      <input buttons type="text" placeholder="Filter Run Log" size="20"
             class="border-none outline-none rounded p-1 text-gray-900 h-8"
             #filterText (input)="cd.markForCheck()">
      <label buttons class="flex items-center gap-1 cursor-pointer border rounded px-1 border-slate-300 h-8">
        Only running
        <input type="checkbox" #onlyRunning
               class="w-5 !text-xl appearance-none font-bold text-transparent checked:text-white codicon codicon-pass cursor-pointer">
      </label>
      <div content *ngrxLet="runLog as runLog" class="h-full overflow-y-auto">
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
                          [gridFormat]="gridFormat" [dateFormat]="dateFormat"></app-run-log-line>
        <p class="text-center p-2 font-semibold" *ngIf="runLog.lines.length === 0">
          No Run Log available or all have been filtered.
        </p>
      </div>
    </app-collapsible-element>
  `,
})
export class RunLogComponent implements OnInit {
  @ViewChild('onlyRunning', {static: true}) onlyRunningCheckbox!: ElementRef<HTMLInputElement>;
  @ViewChild('filterText', {static: true}) filterText!: ElementRef<HTMLInputElement>;
  @ViewChildren(RunLogLineComponent) runLogLines?: QueryList<RunLogLineComponent>;
  protected readonly gridFormat = 'auto / 15ch 15ch 1fr auto auto';
  protected readonly dateFormat = 'MM-dd HH:mm:ss';

  constructor(private store: Store,
              private datePipe: DatePipe,
              protected cd: ChangeDetectorRef) {}

  get runLog() {
    return this.store.select(DetailsSelectors.runLog).pipe(map(runLog => produce(runLog, draft => {
      if(this.onlyRunningCheckbox.nativeElement.checked) draft.lines = draft.lines.filter(line => line.end === undefined);
      if(this.filterText.nativeElement.value !== undefined) {
        draft.lines = draft.lines.filter(line => {
          const filterText = this.filterText.nativeElement.value;
          return this.datePipe.transform(line.end, this.dateFormat)?.includes(filterText) ||
                 this.datePipe.transform(line.start, this.dateFormat)?.includes(filterText) ||
                 line.command.command.toLowerCase().includes(filterText.toLowerCase());
        });
      }
      draft.lines.sort((a, b) => new Date(a.start).valueOf() - new Date(b.start).valueOf());
    })));
  }

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
