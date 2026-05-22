import { ChangeDetectionStrategy, Component, inject, input, OnDestroy, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { ProcessPlotComponent } from './process-plot.component';

@Component({
  selector: 'app-process-plot-container',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CollapsibleElementComponent,
    ProcessPlotComponent
  ],
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [initialContentHeight]="670" [contentOverflow]="true"
                             (collapseStateChanged)="isCollapsed = $event" [codiconName]="'codicon-graph-line'">
      @if (isZoomed()) {
        <button buttons (click)="onResetZoom()"
                class="bg-stone-50 text-black border border-1 border-gray-400 rounded pl-2.5 pr-3 py-0.5 flex items-center">
          <span class="codicon codicon-zoom-out mr-1.5"></span> Reset zoom
        </button>
      }
      @if (axesAreOverridden()) {
        <button buttons (click)="onResetAxes()"
                class="bg-stone-50 text-black border border-1 border-gray-400 rounded pl-2.5 pr-3 py-0.5 flex items-center">
          <span class="codicon codicon-discard mr-1.5"></span> Reset axes
        </button>
      }
      @if (!isCollapsed) {
        <app-process-plot content class="block w-full h-full relative" />
      }
    </app-collapsible-element>
  `
})
export class ProcessPlotContainerComponent implements OnInit, OnDestroy {
  readonly unitId = input<string>();
  readonly recentRunId = input<string>();
  protected isCollapsed = false;
  private store = inject(Store);
  protected isZoomed = this.store.selectSignal(ProcessPlotSelectors.anySubplotZoomed);
  protected axesAreOverridden = this.store.selectSignal(ProcessPlotSelectors.axesAreOverridden);

  ngOnInit() {
    const unitId = this.unitId();
    if(unitId !== undefined) this.store.dispatch(ProcessPlotActions.processPlotComponentInitializedForUnit({unitId: unitId}));
    const recentRunId = this.recentRunId();
    if(recentRunId !== undefined) {
      this.store.dispatch(ProcessPlotActions.processPlotComponentInitializedForRecentRun({recentRunId: recentRunId}));
    }
  }

  ngOnDestroy() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentDestroyed());
  }

  onResetAxes() {
    this.store.dispatch(ProcessPlotActions.processPlotAxesReset());
  }

  onResetZoom() {
    this.store.dispatch(ProcessPlotActions.processPlotZoomReset());
  }
}
