import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import { axisBottom, axisLeft, axisRight, line, ScaleLinear, scaleLinear, select, Selection } from 'd3';
import { combineLatest, filter, Subject, take, takeUntil } from 'rxjs';
import { PlotConfiguration, ProcessValue } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';

@Component({
  selector: 'app-process-plot-d3',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400"
                             (collapseStateChanged)="isCollapsed = $event">
      <svg content class="h-full w-full" #plot *ngIf="!isCollapsed"></svg>
    </app-collapsible-element>
  `,
})
export class ProcessPlotD3Component implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('plot', {static: false}) plotElement?: ElementRef<SVGSVGElement>;
  protected isCollapsed = false;
  private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration).pipe(filter(UtilMethods.isNotNullOrUndefined));
  private processValuesLog = this.store.select(DetailsSelectors.processValuesLog);
  private plots = combineLatest([this.plotConfiguration, this.processValuesLog]);
  private xScale = scaleLinear();
  private yScales: ScaleLinear<number, number>[] = [];
  private svg?: Selection<SVGSVGElement, unknown, null, any>;
  private componentDestroyed = new Subject<void>();

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentInitialized());
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  ngAfterViewInit() {
    this.plots.pipe(take(1)).subscribe(([plotConfiguration, processValuesLog]) => {
      if(this.plotElement === undefined) return;
      this.svg = select<SVGSVGElement, unknown>(this.plotElement?.nativeElement);

      const resizeObserver = new ResizeObserver(() => {
        this.onResize(plotConfiguration);
      });
      resizeObserver.observe(this.plotElement?.nativeElement);

      this.firstTimeSetup(plotConfiguration);

      this.processValuesLog.pipe(takeUntil(this.componentDestroyed)).subscribe((processValuesLog) => {
        this.xScale.domain([0, processValuesLog.length]);

        this.produceData(plotConfiguration, processValuesLog);
      });
    });
  }


  produceData(plotConfiguration: PlotConfiguration,
              processValuesLog: ProcessValue[][]) {
    return plotConfiguration.sub_plots.flatMap((subPlot, subPlotIndex) => {
      if(subPlotIndex !== 0) return; // TODO: multiple subplots
      const values = subPlot.axes.flatMap((axis, axisIndex) => {
        const values = axis.process_value_names.map(name => {
          return processValuesLog
            .map(processValues => processValues.find(processValue => processValue.name === name)?.value)
            .filter(UtilMethods.isNotNullOrUndefined).filter(UtilMethods.isNumber)
            .map<[number, number]>((processValue, valueIndex) => [valueIndex, processValue]);
        });

        this.svg?.select<SVGGElement>('.graph')
          .selectAll('path')
          .data(values)
          .join('path')
          .attr('d', d => line()
            .x(d => this.xScale(d[0]))
            .y(d => this.yScales[axisIndex](d[1]))
            (d),
          )
          .attr('stroke', '#333')
          .attr('stroke-width', 1)
          .attr('fill', 'none');

        return values;
      });

      // TODO: multiple subplots
      const maxXValue = Math.max(...values[0].map(([valueIndex, _]) => valueIndex));
      this.xScale.domain([0, maxXValue]);
      this.svg?.select<SVGGElement>('.x-axis').call(axisBottom(this.xScale));
    });
  }

  private firstTimeSetup(plotConfiguration: PlotConfiguration) {
    // TODO: multiple subplots
    this.yScales = plotConfiguration.sub_plots[0].axes.map(axis => scaleLinear()
      .domain([axis.y_min, axis.y_max]),
    );

    this.svg?.append('g').attr('class', 'x-axis');
    plotConfiguration.sub_plots[0].axes.forEach((axis, axisIndex) => {
      this.svg?.append('g').attr('class', `y-axis-${axisIndex}`);
    });

    this.svg?.append('g').attr('class', 'graph');

    this.onResize(plotConfiguration);
  }

  private onResize(plotConfiguration: PlotConfiguration) {
    const height = this.svg?.node()?.height.baseVal.value ?? 0;
    const width = this.svg?.node()?.width.baseVal.value ?? 0;
    const margin = {left: 0, top: 10, right: 0, bottom: 0};
    const axisSpace = 35;

    this.yScales.forEach(yScale => yScale.range([margin.top, height - margin.bottom - axisSpace]));
    this.xScale.range([margin.left + axisSpace, width - margin.right - axisSpace]);

    this.svg?.select<SVGGElement>('.x-axis')
      .attr('transform', `translate(${[0, height - margin.bottom - axisSpace]})`)
      .call(axisBottom(this.xScale));

    // TODO: multiple subplots
    plotConfiguration.sub_plots[0].axes.forEach((axis, axisIndex) => {
      const yScale = this.yScales[axisIndex];
      const xTransform = axisIndex === 0 ? margin.left + axisSpace : width - margin.right - axisSpace;
      this.svg?.select<SVGGElement>(`.y-axis-${axisIndex}`)
        .attr('transform', `translate(${[xTransform, 0]})`)
        .call(axisIndex === 0 ? axisLeft(yScale) : axisRight(yScale));
    });
  }
}
