import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import { Chart } from 'chart.js';
import { filter, Subject, takeUntil } from 'rxjs';
import { PlotConfiguration, ProcessValue } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';

@Component({
  selector: 'app-process-plot-chartjs',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400" (collapseStateChanged)="collapsed = $event">
      <canvas content class="h-full" #plot *ngIf="!collapsed"></canvas>
    </app-collapsible-element>`,
})
export class ProcessPlotChartjsComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('plot', {static: false}) plotElement?: ElementRef<HTMLCanvasElement>;
  protected collapsed = false;
  private processValuesLog = this.store.select(DetailsSelectors.processValuesLog);
  private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration);
  private componentDestroyed = new Subject<void>();
  private chart?: Chart;

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentInitialized());
  }

  ngAfterViewInit() {
    this.plotConfiguration.pipe(filter(UtilMethods.isNotNullOrUndefined), takeUntil(this.componentDestroyed)).subscribe(plotConfiguration => {
      this.processValuesLog.pipe(takeUntil(this.componentDestroyed)).subscribe(processValueLog => {
        this.setupChart(plotConfiguration, processValueLog);
      });
    });
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  private setupChart(plotConfiguration: PlotConfiguration, processValueLog: ProcessValue[][]) {
    if(this.plotElement === undefined) throw Error('missing plot dom element!');
    const element = this.plotElement?.nativeElement;
    this.chart = new Chart(element, {
      type: 'line',
      data: {
        labels: [],
        datasets: [],
      },
    });
  }
}
