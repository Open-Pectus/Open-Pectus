import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { map } from 'rxjs';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';

@Component({
  selector: 'app-run-log',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Run Log'" [heightResizable]="true" (contentHeightChanged)="onContentHeightChanged($event)">
      <div content *ngrxLet="runLog as runLog">
        <div class="grid bg-slate-200 gap-2 px-3 py-2" [style.grid]="gridFormat | ngrxPush">
          <b>Start</b>
          <b>End</b>
          <b>Command</b>
          <b *ngFor="let additionalColumn of runLog.additional_columns">
            {{additionalColumn.header}}
          </b>
        </div>
        <app-run-log-line *ngFor="let runLogLine of runLog.lines; let index = index" [runLogLine]="runLogLine" [index]="index"
                          [gridFormat]="gridFormat | ngrxPush" [additionalColumns]="runLog.additional_columns"></app-run-log-line>
      </div>
    </app-collapsible-element>
  `,
})
export class RunLogComponent implements OnInit {
  contentHeight = 400;
  runLog = this.store.select(DetailsSelectors.runLog);
  gridFormat = this.runLog.pipe(map(runLog => {
    return `auto / 1fr 1fr 2fr repeat(${runLog.additional_columns.length}, 1fr)`;
  }));

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.runLogComponentInitialized());
  }

  onContentHeightChanged(newHeight: number) {
    this.contentHeight = newHeight;
  }
}
