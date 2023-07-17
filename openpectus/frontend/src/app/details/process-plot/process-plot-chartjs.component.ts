import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { concatLatestFrom } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import {
  CategoryScale,
  Chart,
  ChartType,
  ChartTypeRegistry,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  ScaleOptionsByType,
  TitleOptions,
  Tooltip,
} from 'chart.js';
import { combineLatest, filter, Subject, take, takeUntil } from 'rxjs';
import { PlotAxis, PlotConfiguration, ProcessValue, SubPlot } from '../../api';
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
  private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration).pipe(filter(UtilMethods.isNotNullOrUndefined));
  private plots = combineLatest([this.processValuesLog, this.plotConfiguration]);
  private componentDestroyed = new Subject<void>();
  private chart?: Chart;

  constructor(private store: Store) {
    Chart.register(LineController, CategoryScale, LinearScale, PointElement, LineElement, Tooltip);
  }

  ngOnInit() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentInitialized());
  }

  ngAfterViewInit() {
    this.plotConfiguration.pipe(take(1)).subscribe(plotConfiguration => {
      this.setupChart(plotConfiguration);
    });
    this.processValuesLog.pipe(
      concatLatestFrom(() => this.plotConfiguration),
      takeUntil(this.componentDestroyed),
    ).subscribe(([processValueLog, plotConfiguration]) => {
      this.updateData(processValueLog, plotConfiguration);
    });
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  private setupChart(plotConfiguration: PlotConfiguration) {
    if(this.plotElement === undefined) throw Error('missing plot dom element!');
    const element = this.plotElement?.nativeElement;
    this.chart = new Chart(element, {
      type: 'line',
      options: {
        animation: false,
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index',
        },
        plugins: {
          // tooltip: {
          //   enabled: true,
          //   position: 'nearest',
          // },
        },
        scales: this.produceScales(plotConfiguration),
      },
      data: {
        labels: [],
        datasets: [],
      },
    });
  }

  private produceScales(plotConfiguration: PlotConfiguration) {
    const maxYAxes = Math.max(...plotConfiguration.sub_plots.map(subPlot => subPlot.axes.length));

    const scales = Object.assign({}, ...plotConfiguration.sub_plots.flatMap(subPlot => {
      const realAxes = subPlot.axes.map((axis, axisIndex) => {
        return this.produceScale(axis, axisIndex, subPlot);
      });

      // const paddingAxes: Partial<ScaleOptionsByType<ChartTypeRegistry[ChartType]['scales']>>[] = [];
      for(let i = subPlot.axes.length; i < maxYAxes; i++) {
        realAxes.push(this.produceScale(subPlot.axes[0], i, subPlot, true));
      }
      // const paddingAxes = new Array(maxYAxes - subPlot.axes.length).fill(undefined).map((_, index) => {
      //   return this.produceScale(subPlot.axes[0], index, subPlot);
      // });
      return realAxes; // .concat(paddingAxes);
    }));
    return scales;
  }

  private produceScale(axis: PlotAxis, axisIndex: number,
                       subPlot: SubPlot, isPadding: boolean = false): Partial<ScaleOptionsByType<ChartTypeRegistry[ChartType]['scales']>> {
    const color = isPadding ? '#555555' : axis.color;
    const label = isPadding ? `${axis.label}_padding_${axisIndex}` : `${axis.label}`;
    return {
      [label]: {
        type: 'linear',
        axis: 'y',
        position: axisIndex === 0 ? 'left' : 'right',
        grid: {display: axisIndex === 0},
        min: axis.y_min,
        max: axis.y_max,
        stack: 'stack',
        stackWeight: subPlot.ratio,
        parsing: false,
        title: {
          text: label,
          color: color,
          display: true,
        } as Partial<TitleOptions>,
        border: {color: color},
        ticks: {color: color},
      }, // as Partial<ScaleOptionsByType<ChartTypeRegistry[ChartType]['scales']>>,
    };
  }

  private updateData(processValueLog: ProcessValue[][], plotConfiguration: PlotConfiguration) {
    if(this.chart === undefined) return;
    this.chart.data = {
      labels: processValueLog.map((_, index) => index),
      datasets: this.produceDataSets(plotConfiguration, processValueLog),
    };
    this.chart.update();
  }

  private produceDataSets(plotConfiguration: PlotConfiguration, processValueLog: ProcessValue[][]) {
    return plotConfiguration.sub_plots.flatMap((subPlot, subPlotIndex) => {
      return subPlot.axes.flatMap(axis => {
        return axis.process_value_names.map(name => {
          return {
            type: 'line',
            label: name,
            pointStyle: false,
            borderColor: axis.color,
            borderWidth: 1,
            data: processValueLog
              .map(processValues => processValues.find(processValue => processValue.name === name)?.value)
              .filter(UtilMethods.isNotNullOrUndefined).filter(UtilMethods.isNumber),
            yAxisID: axis.label,
          } as const;
        });
      });
    });
  }
}
