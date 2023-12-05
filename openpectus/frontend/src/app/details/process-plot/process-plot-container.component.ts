import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input, OnDestroy, OnInit } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { ProcessPlotComponent } from './process-plot.component';

@Component({
  selector: 'app-process-plot-container',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    CollapsibleElementComponent,
    NgIf,
    ProcessPlotComponent,
    PushPipe,
  ],
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
export class ProcessPlotContainerComponent implements OnInit, OnDestroy {
  @Input() unitId?: string;
  @Input() batchJobId?: string;

  protected isCollapsed = false;
  protected plotIsModified = this.store.select(ProcessPlotSelectors.plotIsModified);

  constructor(private store: Store) {}

  ngOnInit() {
    if(this.unitId !== undefined) this.store.dispatch(ProcessPlotActions.processPlotComponentInitializedForUnit({unitId: this.unitId}));
    if(this.batchJobId !== undefined) {
      this.store.dispatch(ProcessPlotActions.processPlotComponentInitializedForBatchJob({batchJobId: this.batchJobId}));
    }
  }

  ngOnDestroy() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentDestroyed());
  }

  onReset() {
    this.store.dispatch(ProcessPlotActions.processPlotReset());
  }
}
