import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import { Layout } from 'plotly.js';
import Plotly, { LayoutAxis, PlotData } from 'plotly.js-basic-dist-min';
import { combineLatest, filter, map, Subject, takeUntil } from 'rxjs';
import { SubPlot } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { PlotlyDefaults } from './plotly-defaults';

@Component({
  selector: 'app-process-plot-plotly',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400" (collapseStateChanged)="collapsed = $event">
      <div content class="h-full" #plot *ngIf="!collapsed"></div>
    </app-collapsible-element>`,
})
export class ProcessPlotPlotlyComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('plot', {static: false}) plotElement?: ElementRef<HTMLDivElement>;
  protected collapsed = false;
  private processValuesLog = this.store.select(DetailsSelectors.processValuesLog);
  private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration);
  private plots = combineLatest([this.processValuesLog, this.plotConfiguration]).pipe(map(([processValueLog, plotConfiguration]) => {
    if(plotConfiguration === undefined) return [];
    return plotConfiguration.sub_plots.flatMap((subPlot, subPlotIndex) => {
      return subPlot.axes.flatMap((axis, axisIndex) => {
        return axis.process_value_names.map(processValueName => {
          return {
            x: processValueLog.map((_, index) => index), // TODO: should be timestamp
            y: processValueLog.map(processValues => processValues.find(processValue => processValue.name === processValueName)?.value),
            yaxis: 'y' + this.mapAxisIndex(subPlotIndex),
            type: 'scatter',
            xaxis: 'x',
            name: processValueName,
          } as Partial<PlotData>;
        });
      });
    });
  }));

  private layout = this.plotConfiguration.pipe(map(plotConfiguration => {
    if(plotConfiguration === undefined) return undefined;
    return {
      grid: {
        rows: plotConfiguration.sub_plots.length,
        columns: 1,
        subplots: plotConfiguration.sub_plots.map((subPlot, subPlotIndex) => {
          return subPlot.axes.map((axis, axisIndex) => `xy${(this.mapAxisIndex(axisIndex + subPlotIndex))}`);
        }),
        yaxes: this.convertToAxes(plotConfiguration.sub_plots), // plotConfiguration?.sub_plots.flatMap(subPlot => this.convertToAxes(subPlot.axes.map(axis => axis.label)))
        roworder: 'top to bottom',
        ygap: 10,
        uirevision: 'true',
        autosize: true,
      },
    } as unknown as Partial<Layout>; // type of subplots is a lie according to documentation
  }));
  private componentDestroyed = new Subject<void>();

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentInitialized());
  }

  ngAfterViewInit() {
    if(this.plotElement === undefined) throw Error('missing plot dom element!');
    const element = this.plotElement?.nativeElement;
    this.layout.pipe(filter(UtilMethods.isNotNullOrUndefined), takeUntil(this.componentDestroyed)).subscribe(layout => {
      this.plots.pipe(takeUntil(this.componentDestroyed)).subscribe(plots => {
        Plotly.react(element, plots, layout, {responsive: true});
      });
    });
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  private mapAxisIndex(axisIndex: number) {
    return axisIndex > 0 ? axisIndex + 1 : '';
  }

  private convertToAxes(subPlots: SubPlot[]) {
    const object = {};
    subPlots.forEach((subPlot, subPlotIndex) => {
      subPlot.axes.forEach((axis, axisIndex) => {
        Object.assign(object, {
          ['yaxis' + this.mapAxisIndex(axisIndex + subPlotIndex)]: {
            title: axis.label,
            side: (axisIndex > 0 ? 'right' : 'left'),
            overlaying: axisIndex > 0 ? 'y' : 'free',
            anchor: axisIndex > 1 ? 'free' : undefined,
            position: axisIndex > 1 ? 1 : undefined,
            titlefont: {color: PlotlyDefaults.colors[subPlotIndex]},
            tickfont: {color: PlotlyDefaults.colors[subPlotIndex]},
            range: [axis.y_min, axis.y_max],
          } as Partial<LayoutAxis>,
        });
      });
    });
    return object;
  }
}
