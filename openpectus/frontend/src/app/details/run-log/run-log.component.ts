import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { map } from 'rxjs';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';

@Component({
  selector: 'app-run-log',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Run Log'" [heightResizable]="true" [contentHeight]="400">
      <div content *ngrxLet="runLog as runLog" class="h-full">
        <div class="grid bg-gray-700 text-white gap-2 px-3 py-2" [style.grid]="gridFormat | ngrxPush">
          <b>Start</b>
          <b>End</b>
          <b>Command</b>
        </div>
        <app-run-log-line *ngFor="let runLogLine of runLog.lines; let index = index" [runLogLine]="runLogLine" [rowIndex]="index"
                          [gridFormat]="gridFormat | ngrxPush" [additionalColumns]="runLog.additional_columns"></app-run-log-line>
      </div>
    </app-collapsible-element>
  `,
})
export class RunLogComponent implements OnInit {
  runLog = this.store.select(DetailsSelectors.runLog);
  gridFormat = this.runLog.pipe(map(runLog => {
    return `auto / 15ch 15ch 1fr`;
  }));

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.runLogComponentInitialized());
  }
}
