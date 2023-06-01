import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';

@Component({
  selector: 'app-run-log',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Run Log'" [heightResizable]="true" (contentHeightChanged)="onContentHeightChanged($event)">
      <app-run-log-line content *ngFor="let runLogLine of (runLogLines | ngrxPush)" [runLogLine]="runLogLine"></app-run-log-line>
    </app-collapsible-element>
  `,
})
export class RunLogComponent implements OnInit {
  contentHeight = 400;
  runLogLines = this.store.select(DetailsSelectors.runLogLines);

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.runLogComponentInitialized());
  }

  onContentHeightChanged(newHeight: number) {
    this.contentHeight = newHeight;
  }
}
