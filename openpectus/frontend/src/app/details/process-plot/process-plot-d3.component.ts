import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, Input, OnDestroy, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import { axisBottom, axisLeft, axisRight, line, ScaleLinear, scaleLinear, select, Selection, sum } from 'd3';
import { filter, Subject, take, takeUntil } from 'rxjs';
import { PlotConfiguration, ProcessValue } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';

@Component({
  selector: 'app-process-plot-d3',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <svg class="h-full w-full" #plot></svg>
  `,
})
export class ProcessPlotD3Component implements OnDestroy, AfterViewInit {
  @ViewChild('plot', {static: false}) plotElement?: ElementRef<SVGSVGElement>;
  @Input() isCollapsed = false;
  private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration).pipe(filter(UtilMethods.isNotNullOrUndefined));
  private processValuesLog = this.store.select(DetailsSelectors.processValuesLog);
  private xScale = scaleLinear();
  private yScales: ScaleLinear<number, number>[][] = [];
  private svg?: Selection<SVGSVGElement, unknown, null, any>;
  private componentDestroyed = new Subject<void>();

  // Configurable values
  private readonly subPlotGap = 20; // also adds to top margin
  private readonly margin = {left: 5, top: 10 - this.subPlotGap, right: 5, bottom: 5};
  private readonly axisGap = 10;

  constructor(private store: Store) {}

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
    const resizeObserver = new ResizeObserver((entries) => {
      // when collapsing, contentRect is 0 width and height, and errors will occur if we try placing elements.
      if(entries.some(entry => entry.contentRect.height === 0)) return;
      this.updateElementPlacements(plotConfiguration);
      this.processValuesLog.pipe(take(1)).subscribe(processValueLog => this.plotData(plotConfiguration, processValueLog));
    });
    resizeObserver.observe(element);
  }

  private plotData(plotConfiguration: PlotConfiguration,
                   processValuesLog: ProcessValue[][]) {
    if(this.svg === undefined) return;
    const svg = this.svg;

    const maxXValue = processValuesLog.length - 1; // TODO: when x is time instead of index, change this to match.
    this.xScale.domain([0, maxXValue]);
    svg.select<SVGGElement>('.x-axis').call(axisBottom(this.xScale));

    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
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
            .y(d => this.yScales[subPlotIndex][axisIndex](d[1])),
          )
          .attr('stroke-width', 1).attr('fill', 'none');
      });
    });
  }

  private firstTimeSetup(plotConfiguration: PlotConfiguration) {
    if(this.svg === undefined) return;
    const svg = this.svg;

    this.yScales = plotConfiguration.sub_plots.map(subPlot => {
      return subPlot.axes.map(axis => {
        return scaleLinear().domain([axis.y_min, axis.y_max]);
      });
    });

    svg.append('g').attr('class', 'x-axis');

    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = svg.append('g').attr('class', `subplot subplot-${subPlotIndex}`);
      subPlot.axes.forEach((axis, axisIndex) => {
        subPlotG.append('g').attr('class', `y-axis y-axis-${axisIndex}`).style('color', axis.color);
        subPlotG.append('g').attr('class', `line line-${axisIndex}`).attr('stroke', axis.color);
        subPlotG.append('rect').attr('class', 'subplot-border');
      });
    });

    this.updateElementPlacements(plotConfiguration);
  }

  private updateElementPlacements(plotConfiguration: PlotConfiguration) {
    if(this.svg === undefined) return;
    const svg = this.svg;
    const svgHeight = this.svg.node()?.height.baseVal.value ?? 0;
    const svgWidth = this.svg.node()?.width.baseVal.value ?? 0;
    const xAxisHeight = svg.select<SVGGElement>('.x-axis').node()?.getBoundingClientRect().height ?? 0;
    const svgPlotsHeight = svgHeight - this.margin.top - this.margin.bottom - xAxisHeight;
    const widestLeftSideYAxisWidth = svg.select<SVGGElement>('.y-axis-0').nodes()
                                       .map(yAxis => yAxis.getBoundingClientRect().width)
                                       .reduce((current, previous) => current + previous + this.axisGap, 0) - this.axisGap;

    const rightSideYAxesWidths = plotConfiguration.sub_plots.map((_, subPlotIndex) => {
      const subPlotG = svg.selectChild(`.subplot-${subPlotIndex}`);
      return subPlotG.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
               .filter((_, index) => index > 0)
               .map(yAxis => yAxis.getBoundingClientRect().width)
               .reduce((current, previous) => current + previous + this.axisGap, 0) - this.axisGap;
    });
    const maxRightSideYAxisWidth = Math.max(...rightSideYAxesWidths, 0);

    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = svg.selectChild(`.subplot-${subPlotIndex}`);

      // Y axes heights
      const totalRatio = sum(plotConfiguration.sub_plots.map(subPlot => subPlot.ratio));
      const previousSubPlotsRatio = sum(plotConfiguration.sub_plots
        .filter((_, index) => index < subPlotIndex)
        .map(subPlot => subPlot.ratio),
      );
      const followingSubPlotsRatio = sum(plotConfiguration.sub_plots
        .filter((_, index) => index > subPlotIndex)
        .map(subPlot => subPlot.ratio),
      );
      const subPlotStartOffset = (previousSubPlotsRatio / totalRatio) * svgPlotsHeight;
      const subPlotEndOffset = (followingSubPlotsRatio / totalRatio) * svgPlotsHeight;
      const subPlotTop = this.margin.top + subPlotStartOffset + this.subPlotGap;
      const subPlotBottom = svgHeight - this.margin.bottom - xAxisHeight - subPlotEndOffset;
      const subPlotLeft = this.margin.left + widestLeftSideYAxisWidth;
      const subPlotRight = svgWidth - this.margin.right - maxRightSideYAxisWidth;
      this.yScales[subPlotIndex].forEach(yScale => yScale.range([subPlotTop, subPlotBottom]));

      // Draw y axes
      subPlot.axes.forEach((axis, axisIndex) => {
        const yScale = this.yScales[subPlotIndex][axisIndex];
        const otherRightSideYAxesWidth = subPlotG.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
                                           .filter((_, otherAxisIndex) => otherAxisIndex !== 0 && otherAxisIndex < axisIndex)
                                           .map(yAxis => yAxis.getBoundingClientRect().width)
                                           .reduce((current, previous) => current + previous + this.axisGap, 0) ?? 0;

        const xTransform = axisIndex === 0 ? subPlotLeft : subPlotRight + otherRightSideYAxesWidth; // right side

        subPlotG.selectChild<SVGGElement>(`.y-axis-${axisIndex}`)
          .call(axisIndex === 0 ? axisLeft(yScale) : axisRight(yScale))
          .attr('transform', `translate(${[xTransform, 0]})`);
      });

      // Draw a rectangle around subplot
      subPlotG.selectChild<SVGGElement>('.subplot-border')
        .attr('stroke-width', 1)
        .attr('stroke', 'black')
        .attr('fill', 'none')
        .attr('x', subPlotLeft)
        .attr('y', subPlotTop)
        // Math.abs() avoids errors with negative values while container is collapsing
        .attr('height', Math.abs(subPlotBottom - subPlotTop))
        .attr('width', Math.abs(subPlotRight - subPlotLeft));
    });

    // Scale x-axis
    this.xScale.range([this.margin.left + widestLeftSideYAxisWidth, svgWidth - this.margin.right - maxRightSideYAxisWidth]);

    // Draw x-axis
    svg.selectChild<SVGGElement>('.x-axis')
      .call(axisBottom(this.xScale))
      .attr('transform', (_, __, selection) => {
        const thisAxisHeight = selection[0].getBoundingClientRect().height;
        return `translate(${[0, svgHeight - this.margin.bottom - thisAxisHeight]})`;
      });
  }
}
