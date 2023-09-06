import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';

@Component({
  selector: 'app-process-plot-container',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400" [contentOverflow]="true"
                             (collapseStateChanged)="isCollapsed = $event">
      <button *ngIf="plotIsModified | ngrxPush" buttons (click)="onReset()" class="bg-rose-900 rounded px-3 py-1">Reset</button>
      <app-process-plot-d3 content class="block w-full h-full relative" *ngIf="!isCollapsed"
                           [isCollapsed]="isCollapsed"></app-process-plot-d3>
    </app-collapsible-element>
  `,
})
export class ProcessPlotContainerComponent implements OnInit {
  protected isCollapsed = false;
  protected plotIsModified = this.store.select(ProcessPlotSelectors.plotIsModified);

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentInitialized());
  }

  onReset() {
    this.store.dispatch(ProcessPlotActions.processPlotReset());
  }
}
