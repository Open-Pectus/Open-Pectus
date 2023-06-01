import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';

@Component({
  selector: 'app-run-log',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Run Log'" [heightResizable]="true" (contentHeightChanged)="onContentHeightChanged($event)">
      <div content>
        <div class="grid grid-cols-3 bg-slate-200 gap-2 px-3 py-2" [style.grid]="gridFormat">
          <b>Start</b>
          <b>End</b>
          <b>Command</b>
        </div>
        <app-run-log-line *ngFor="let runLogLine of (runLogLines | ngrxPush); let index = index" [runLogLine]="runLogLine" [index]="index"
                          [gridFormat]="gridFormat"></app-run-log-line>
      </div>
    </app-collapsible-element>
  `,
  // styles: [':host ::ng-deep app-run-log-line:nth-child(odd) .grid { @apply bg-slate-200; }'],
})
export class RunLogComponent implements OnInit {
  contentHeight = 400;
  runLogLines = this.store.select(DetailsSelectors.runLogLines);
  gridFormat = 'auto / 1fr 1fr 2fr';

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.runLogComponentInitialized());
  }

  onContentHeightChanged(newHeight: number) {
    this.contentHeight = newHeight;
  }
}
