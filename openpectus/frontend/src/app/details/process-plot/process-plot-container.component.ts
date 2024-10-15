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
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="670" [contentOverflow]="true"
                             (collapseStateChanged)="isCollapsed = $event" [codiconName]="'codicon-graph-line'">
      <button *ngIf="isZoomed | ngrxPush" buttons (click)="onResetZoom()"
              class="bg-stone-50 text-black border border-1 border-gray-400 rounded pl-2.5 pr-3 py-0.5 flex items-center">
        <span class="codicon codicon-zoom-out mr-1.5"></span> Reset zoom
      </button>
      <button *ngIf="axesAreOverridden | ngrxPush" buttons (click)="onResetAxes()"
              class="bg-stone-50 text-black border border-1 border-gray-400 rounded pl-2.5 pr-3 py-0.5 flex items-center">
        <span class="codicon codicon-discard mr-1.5"></span> Reset axes
      </button>
      <app-process-plot content class="block w-full h-full relative" *ngIf="!isCollapsed"></app-process-plot>
    </app-collapsible-element>
  `,
})
export class ProcessPlotContainerComponent implements OnInit, OnDestroy {
  @Input() unitId?: string;
  @Input() recentRunId?: string;

  protected isCollapsed = false;
  protected isZoomed = this.store.select(ProcessPlotSelectors.anySubplotZoomed);
  protected axesAreOverridden = this.store.select(ProcessPlotSelectors.axesAreOverridden);

  constructor(private store: Store) {}

  ngOnInit() {
    if(this.unitId !== undefined) this.store.dispatch(ProcessPlotActions.processPlotComponentInitializedForUnit({unitId: this.unitId}));
    if(this.recentRunId !== undefined) {
      this.store.dispatch(ProcessPlotActions.processPlotComponentInitializedForRecentRun({recentRunId: this.recentRunId}));
    }
  }

  ngOnDestroy() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentDestroyed());
  }

  onResetAxes() {
    this.store.dispatch(ProcessPlotActions.processPlotAxesReset());
  }

  onResetZoom() {
    this.store.dispatch(ProcessPlotActions.processPlotZoomReset())
  }
}
