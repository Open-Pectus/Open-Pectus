import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, Input, OnDestroy, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import { axisBottom, line, ScaleLinear, scaleLinear, select, Selection } from 'd3';
import { filter, Subject, take, takeUntil } from 'rxjs';
import { PlotAxis, PlotColorRegion, PlotConfiguration } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { ProcessValueLog } from './ngrx/process-plot.reducer';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { ProcessPlotD3Placement } from './process-plot-d3.placement';

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
  private processValuesLog = this.store.select(ProcessPlotSelectors.processValuesLog);
  private xScale = scaleLinear();
  private yScales: ScaleLinear<number, number>[][] = [];
  private svg?: Selection<SVGSVGElement, unknown, null, any>;
  private componentDestroyed = new Subject<void>();
  private placement = new ProcessPlotD3Placement();

  constructor(private store: Store) {}

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  ngAfterViewInit() {
    this.plotConfiguration.pipe(take(1)).subscribe(plotConfiguration => {
      if(this.plotElement === undefined) return;
      this.svg = select<SVGSVGElement, unknown>(this.plotElement.nativeElement);
      this.setupOnResize(plotConfiguration, this.plotElement.nativeElement);
      this.oneTimeSetup(plotConfiguration);
      this.setupOnDataChange(plotConfiguration);
    });
  }

  private setupOnResize(plotConfiguration: PlotConfiguration, element: Element) {
    const resizeObserver = new ResizeObserver((entries) => {
      // when collapsing, contentRect is 0 width and height, and errors will occur if we try placing elements.
      if(entries.some(entry => entry.contentRect.height === 0)) return;
      this.placement.updateElementPlacements(plotConfiguration, this.svg, this.xScale, this.yScales);
      this.processValuesLog.pipe(take(1)).subscribe(processValueLog => this.plotData(plotConfiguration, processValueLog));
    });
    resizeObserver.observe(element);
  }

  private oneTimeSetup(plotConfiguration: PlotConfiguration) {
    if(this.svg === undefined) return;
    this.yScales = this.createYScales(plotConfiguration);
    this.insertSvgElements(this.svg, plotConfiguration);
    this.placement.updateElementPlacements(plotConfiguration, this.svg, this.xScale, this.yScales);
  }

  private createYScales(plotConfiguration: PlotConfiguration) {
    return plotConfiguration.sub_plots.map(subPlot => subPlot.axes.map(axis => {
      return scaleLinear().domain([axis.y_min, axis.y_max]);
    }));
  }

  private insertSvgElements(svg: Selection<SVGSVGElement, unknown, null, any>, plotConfiguration: PlotConfiguration) {
    const root = svg.append('g').attr('class', 'root');
    root.append('g').attr('class', 'x-axis');
    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = root.append('g').attr('class', `subplot subplot-${subPlotIndex}`);
      plotConfiguration.color_regions.forEach((colorRegion, colorRegionIndex) => {
        subPlotG.append('g').attr('class', `color-region-${colorRegionIndex}`);
      });
      subPlot.axes.forEach((axis, axisIndex) => {
        subPlotG.append('g').attr('class', `x-grid-lines`).style('color', '#cccccc');
        subPlotG.append('g').attr('class', `y-grid-lines`).style('color', '#cccccc');
        subPlotG.append('g').attr('class', `y-axis y-axis-${axisIndex}`).style('color', axis.color);
        subPlotG.append('text').attr('class', `axis-label axis-label-${axisIndex}`).attr('fill', axis.color)
          .style('font-size', this.placement.axisLabelHeight).text(axis.label);
        subPlotG.append('g').attr('class', `line line-${axisIndex}`).attr('stroke', axis.color);
        subPlotG.append('rect').attr('class', 'subplot-border');
      });
    });
  }

  private setupOnDataChange(plotConfiguration: PlotConfiguration) {
    this.processValuesLog.pipe(takeUntil(this.componentDestroyed)).subscribe(processValuesLog => {
      this.plotData(plotConfiguration, processValuesLog);
    });
  }

  private plotData(plotConfiguration: PlotConfiguration,
                   processValuesLog: ProcessValueLog) {
    if(this.svg === undefined) throw Error('no Svg selection when plotting data!');
    this.updateXScaleDomain(plotConfiguration, processValuesLog, this.svg);
    this.plotLines(plotConfiguration, processValuesLog, this.svg);
    this.plotRectangles(plotConfiguration, processValuesLog, this.svg);
  }

  private updateXScaleDomain(plotConfiguration: PlotConfiguration, processValuesLog: ProcessValueLog,
                             svg: Selection<SVGSVGElement, unknown, null, any>) {
    const maxXValue = (Object.values(processValuesLog)[0]?.length ?? 1) - 1; // TODO: when x is time instead of index, change this to match.
    this.xScale.domain([0, maxXValue]);
    svg.select<SVGGElement>('.x-axis').call(axisBottom(this.xScale));
    plotConfiguration.sub_plots.forEach((_, subPlotIndex) => {
      svg.select<SVGGElement>(`.subplot-${subPlotIndex} .x-grid-lines`).call(this.placement.xGridLineAxisGenerators[subPlotIndex]);
    });
  }

  private plotLines(plotConfiguration: PlotConfiguration, processValuesLog: ProcessValueLog,
                    svg: Selection<SVGSVGElement, unknown, null, any>) {
    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      subPlot.axes.forEach((axis, axisIndex) => {
        svg.select<SVGGElement>(`.subplot-${subPlotIndex} .line-${axisIndex}`)
          .selectAll('path')
          .data(this.formatLineDataForAxis(processValuesLog, axis))
          .join('path')
          .attr('d', line()
            .x(d => this.xScale(d[0]))
            .y(d => this.yScales[subPlotIndex][axisIndex](d[1])),
          )
          .attr('stroke-width', 1)
          .attr('fill', 'none');
      });
    });
  }

  private plotRectangles(plotConfiguration: PlotConfiguration, processValueLog: ProcessValueLog,
                         svg: Selection<SVGSVGElement, unknown, null, any>) {
    plotConfiguration.color_regions.forEach((colorRegion, colorRegionIndex) => {
      const topColorRegionSelection = svg.select<SVGGElement>(`.color-region-${colorRegionIndex}`);
      const formattedRectData = this.formatRectData(colorRegion, processValueLog);
      const top = this.yScales[0][0].range()[1];
      plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
        const colorRegionSelection = svg.select<SVGGElement>(`.subplot-${subPlotIndex} .color-region-${colorRegionIndex}`);
        const subPlotTop = this.yScales[subPlotIndex][0].range()[1];
        const subPlotBottom = this.yScales[subPlotIndex][0].range()[0];
        if(subPlotBottom < 0) return; // while expanding, this can be temporarily negative throwing errors in console. So let's avoid that.

        // Rectangle
        colorRegionSelection.selectAll('rect')
          .data(formattedRectData)
          .join('rect')
          .attr('x', d => this.xScale(d.start))
          .attr('y', subPlotTop)
          .attr('width', d => this.xScale(d.end) - this.xScale(d.start))
          .attr('height', subPlotBottom - subPlotTop)
          .attr('fill', d => d.color);
      });

      // Arrow
      topColorRegionSelection.selectAll('path')
        .data(formattedRectData)
        .join('path')
        .attr('transform', d => `translate(${[this.xScale(d.end) - (this.xScale(d.end) - this.xScale(d.start)) / 2, top]})`)
        .attr('d', 'M -6 -12 0 -9 6 -12 0 0')
        .attr('fill', 'black');

      // Label
      topColorRegionSelection.selectAll('text')
        .data(formattedRectData)
        .join('text')
        .attr('transform',
          d => `translate(${[this.xScale(d.end) - (this.xScale(d.end) - this.xScale(d.start)) / 2 + 3, top - 14]}) rotate(-90)`)
        .style('font-size', 11)
        .text(d => d.value ?? '')
        .attr('fill', 'black');
    });

  }

  private formatLineDataForAxis(processValuesLog: ProcessValueLog, axis: PlotAxis): [number, number][][] {
    return axis.process_value_names
      .map(processValueName => processValuesLog[processValueName])
      .filter(UtilMethods.isNotNullOrUndefined)
      .map(processValueLine => processValueLine.map(processValue => processValue.value)
        .filter(UtilMethods.isNumber)
        .map((processValueValue, index) => [index, processValueValue]),
      );
  }

  private formatRectData(colorRegion: PlotColorRegion, processValueLog: ProcessValueLog) {
    const processValueData = processValueLog[colorRegion.process_value_name];
    if(processValueData === undefined) return [];
    const processValueValues = processValueData.map(processValue => processValue.value);
    let start: number = 0;
    const coloredRegionRects: ColoredRegionRect[] = [];
    for(let i = 0; i < processValueValues.length; i++) {
      const currentValueColor = colorRegion.value_color_map[processValueValues[i] ?? -1];
      const previousValueColor = colorRegion.value_color_map[processValueValues[i - 1] ?? -1];
      if(currentValueColor === previousValueColor) continue; // same value, just skip ahead
      if(previousValueColor !== undefined) {
        coloredRegionRects.push({start, end: i, color: previousValueColor, value: processValueValues[i - 1]});
      }
      if(currentValueColor !== undefined) start = i;
    }
    const valueAtEnd = processValueValues[processValueData.length - 1];
    const colorAtEnd = colorRegion.value_color_map[valueAtEnd ?? -1];
    if(colorAtEnd !== undefined) { // we ran past end, but was drawing a rect, so push that into array
      coloredRegionRects.push({start, end: processValueData.length - 1, color: colorAtEnd, value: valueAtEnd});
    }
    return coloredRegionRects;
  }
}


interface ColoredRegionRect {
  start: number;
  end: number;
  color: string;
  value: string | number | undefined;
}