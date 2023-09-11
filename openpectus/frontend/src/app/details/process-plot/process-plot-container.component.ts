import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';

@Component({
  selector: 'app-process-plot-container',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400" [contentOverflow]="true"
                             (collapseStateChanged)="isCollapsed = $event" [codiconName]="'codicon-graph-line'">
      <button *ngIf="plotIsModified | ngrxPush" buttons (click)="onReset()" class="bg-orange-800 rounded pl-2.5 pr-3 py-1 flex items-center">
        <span class="codicon codicon-discard mr-1.5"></span> Reset view
      </button>
      <app-process-plot content class="block w-full h-full relative" *ngIf="!isCollapsed"></app-process-plot>
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
