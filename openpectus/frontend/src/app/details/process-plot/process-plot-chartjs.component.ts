import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import { Subject } from 'rxjs';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';

@Component({
  selector: 'app-process-plot-chartjs',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400" (collapseStateChanged)="collapsed = $event">
      <div content class="h-full" #plot *ngIf="!collapsed"></div>
    </app-collapsible-element>`,
})
export class ProcessPlotChartjsComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('plot', {static: false}) plotElement?: ElementRef<HTMLDivElement>;
  protected collapsed = false;
  private processValuesLog = this.store.select(DetailsSelectors.processValuesLog);
  private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration);
  private componentDestroyed = new Subject<void>();

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentInitialized());
  }

  ngAfterViewInit() {
    if(this.plotElement === undefined) throw Error('missing plot dom element!');
    const element = this.plotElement?.nativeElement;

  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }
}
