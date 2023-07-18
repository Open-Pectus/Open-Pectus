import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import { axisBottom, axisLeft, axisRight, line, ScaleLinear, scaleLinear, select, Selection } from 'd3';
import { filter, Subject, take, takeUntil } from 'rxjs';
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
  private xScale = scaleLinear();
  private yScales: ScaleLinear<number, number>[] = [];
  private svg?: Selection<SVGSVGElement, unknown, null, any>;
  private componentDestroyed = new Subject<void>();

  // Configurable values
  private margin = {left: 5, top: 10, right: 5, bottom: 5};
  private axisGap = 10;

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentInitialized());
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  ngAfterViewInit() {
    this.plotConfiguration.pipe(take(1)).subscribe(plotConfiguration => {
      if(this.plotElement === undefined) return;
      this.svg = select<SVGSVGElement, unknown>(this.plotElement.nativeElement);
      this.setupOnResize(plotConfiguration, this.plotElement.nativeElement);
      this.firstTimeSetup(plotConfiguration);
      this.setupPlotDataOnDataChange(plotConfiguration);
    });
  }

  private setupPlotDataOnDataChange(plotConfiguration: PlotConfiguration) {
    this.processValuesLog.pipe(
      takeUntil(this.componentDestroyed),
    ).subscribe((processValuesLog) => {
      this.plotData(plotConfiguration, processValuesLog);
    });
  }

  private setupOnResize(plotConfiguration: PlotConfiguration, element: Element) {
    const resizeObserver = new ResizeObserver(() => {
      this.updateElementPlacements(plotConfiguration);
    });
    resizeObserver.observe(element);
  }

  private plotData(plotConfiguration: PlotConfiguration,
                   processValuesLog: ProcessValue[][]) {
    if(this.svg === undefined) return;
    const svg = this.svg;

    // TODO: multiple subplots
    const maxXValue = processValuesLog.length - 1; // TODO: when x is time instead of index, change this to match.
    this.xScale.domain([0, maxXValue]);
    svg.select<SVGGElement>('.x-axis').call(axisBottom(this.xScale));

    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      if(subPlotIndex !== 0) return; // TODO: multiple subplots
      subPlot.axes.forEach((axis, axisIndex) => {
        const valuesPerProcessValue = axis.process_value_names.map(name => {
          return processValuesLog
            .map(processValues => processValues.find(processValue => processValue.name === name)?.value)
            .filter(UtilMethods.isNotNullOrUndefined).filter(UtilMethods.isNumber)
            .map<[number, number]>((processValue, valueIndex) => [valueIndex, processValue]);
        });

        svg.select<SVGGElement>(`.subplot-${subPlotIndex} .line-${axisIndex}`)
          .selectAll('path').data(valuesPerProcessValue).join('path')
          .attr('d', line()
            .x(d => this.xScale(d[0]))
            .y(d => this.yScales[axisIndex](d[1])),
          )
          .attr('stroke-width', 1).attr('fill', 'none');
      });
    });
  }

  private firstTimeSetup(plotConfiguration: PlotConfiguration) {
    if(this.svg === undefined) return;
    const svg = this.svg;

    // TODO: multiple subplots
    this.yScales = plotConfiguration.sub_plots[0].axes.map(axis => scaleLinear()
      .domain([axis.y_min, axis.y_max]),
    );

    svg.append('g').attr('class', 'x-axis');
    plotConfiguration.sub_plots[0].axes.forEach((axis, axisIndex) => {
      svg.append('g').attr('class', `y-axis y-axis-${axisIndex}`)
        .style('color', axis.color);
    });

    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = svg.append('g').attr('class', `subplot subplot-${subPlotIndex}`);
      subPlot.axes.forEach((axis, axisIndex) => {
        subPlotG.append('g').attr('class', `line line-${axisIndex}`).attr('stroke', axis.color);
      });
    });

    this.updateElementPlacements(plotConfiguration);
  }

  private updateElementPlacements(plotConfiguration: PlotConfiguration) {
    if(this.svg === undefined) return;
    const svgHeight = this.svg.node()?.height.baseVal.value ?? 0;
    const svgWidth = this.svg.node()?.width.baseVal.value ?? 0;

    // Update scales
    const xAxisHeight = this.svg.selectChild<SVGGElement>('.x-axis').node()?.getBoundingClientRect().height ?? 0;
    const leftSideYAxisWidth = this.svg.selectChild<SVGGElement>('.y-axis').node()?.getBoundingClientRect().width ?? 0;
    const rightSideYAxesWidth = this.svg.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
                                  .filter((_, index) => index > 0)
                                  .map(yAxis => yAxis.getBoundingClientRect().width)
                                  .reduce((current, previous) => current + previous + this.axisGap, 0) - this.axisGap;

    this.yScales.forEach(yScale => yScale.range([this.margin.top, svgHeight - this.margin.bottom - xAxisHeight]));
    this.xScale.range([this.margin.left + leftSideYAxisWidth, svgWidth - this.margin.right - rightSideYAxesWidth]);

    // Draw x-axis
    this.svg.selectChild<SVGGElement>('.x-axis')
      .call(axisBottom(this.xScale))
      .attr('transform', (_, __, selection) => {
        const thisAxisHeight = selection[0].getBoundingClientRect().height;
        return `translate(${[0, svgHeight - this.margin.bottom - thisAxisHeight]})`;
      });

    // Draw y axes
    // TODO: multiple subplots
    plotConfiguration.sub_plots[0].axes.forEach((axis, axisIndex) => {
      const yScale = this.yScales[axisIndex];
      const otherRightSideYAxesWidth = this.svg?.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
                                         .filter((_, otherAxisIndex) => otherAxisIndex > axisIndex)
                                         .map(yAxis => yAxis.getBoundingClientRect().width)
                                         .reduce((current, previous) => current + previous + this.axisGap, 0) ?? 0;

      this.svg?.selectChild<SVGGElement>(`.y-axis-${axisIndex}`)
        .call(axisIndex === 0 ? axisLeft(yScale) : axisRight(yScale))
        .attr('transform', (_, __, selection) => {
          const thisAxisWidth = selection[0].getBoundingClientRect().width;
          const xTransform = axisIndex === 0
                             ? this.margin.left + thisAxisWidth // left side
                             : svgWidth - this.margin.right - thisAxisWidth - otherRightSideYAxesWidth; // right side
          return `translate(${[xTransform, 0]})`;
        });
    });
  }
}
