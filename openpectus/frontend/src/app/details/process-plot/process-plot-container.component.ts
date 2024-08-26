import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, effect, input, Input, OnDestroy, OnInit } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { DetailsQueriesService } from '../details-queries.service';
import { DetailsActions } from '../ngrx/details.actions';
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
      <button *ngIf="plotIsModified | ngrxPush" buttons (click)="onReset()"
              class="bg-red-300 text-black rounded pl-2.5 pr-3 py-1 flex items-center">
        <span class="codicon codicon-discard mr-1.5"></span> Reset view
      </button>
      <app-process-plot content class="block w-full h-full relative" *ngIf="!isCollapsed"></app-process-plot>
    </app-collapsible-element>
  `,
})
export class ProcessPlotContainerComponent implements OnInit, OnDestroy {
  unitId = input<string>('');
  @Input() recentRunId?: string;

  protected isCollapsed = false;
  protected plotIsModified = this.store.select(ProcessPlotSelectors.plotIsModified);

  private processValuesQuery = this.detailsQueriesService.injectProcessValuesQuery();
  private storeFetchedProcessValues = effect(() => {
    if(this.processValuesQuery === undefined) return;
    const processValues = this.processValuesQuery.data();
    if(processValues === undefined) return;
    // setTimeout to break out of the reactive context, which for some reason causes some problems: TODO: figure out why
    setTimeout(() => this.store.dispatch(DetailsActions.processValuesFetched({processValues})));
  });

  constructor(private store: Store,
              private detailsQueriesService: DetailsQueriesService) {}

  ngOnInit() {
    const unitId = this.unitId();
    if(unitId !== undefined) this.store.dispatch(ProcessPlotActions.processPlotComponentInitializedForUnit({unitId}));
    if(this.recentRunId !== undefined) {
      this.store.dispatch(ProcessPlotActions.processPlotComponentInitializedForRecentRun({recentRunId: this.recentRunId}));
    }
  }

  ngOnDestroy() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentDestroyed());
  }

  onReset() {
    this.store.dispatch(ProcessPlotActions.processPlotReset());
  }
}
