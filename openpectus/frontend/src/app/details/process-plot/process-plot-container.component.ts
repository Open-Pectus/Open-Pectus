import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { ProcessPlotActions } from './ngrx/process-plot.actions';

@Component({
  selector: 'app-process-plot-container',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400"
                             (collapseStateChanged)="isCollapsed = $event">
      <app-process-plot-d3 content class="h-full w-full" *ngIf="!isCollapsed" [isCollapsed]="isCollapsed"></app-process-plot-d3>
    </app-collapsible-element>
  `,
})
export class ProcessPlotContainerComponent implements OnInit {
  protected isCollapsed = false;

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentInitialized());
  }
}
