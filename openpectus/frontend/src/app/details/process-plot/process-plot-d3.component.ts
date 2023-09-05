import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, HostBinding, Input, NgZone, OnDestroy, ViewChild } from '@angular/core';
import { concatLatestFrom } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { axisBottom, ScaleLinear, scaleLinear, select } from 'd3';
import { filter, firstValueFrom, identity, Subject, take, takeUntil } from 'rxjs';
import { PlotConfiguration } from '../../api';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';
import { UtilMethods } from '../../shared/util-methods';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessValueLog } from './ngrx/process-plot.reducer';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { ProcessPlotD3ZoomAndPan } from './process-plot-d3-zoom-and.pan';
import { ProcessPlotD3Annotations } from './process-plot-d3.annotations';
import { ProcessPlotD3AxesOverrides } from './process-plot-d3.axes-overrides';
import { ProcessPlotD3ColoredRegions } from './process-plot-d3.colored-regions';
import { ProcessPlotD3FontSizes } from './process-plot-d3.font-sizes';
import { ProcessPlotD3Lines } from './process-plot-d3.lines';
import { ProcessPlotD3Placement } from './process-plot-d3.placement';
import { ProcessPlotD3Tooltip } from './process-plot-d3.tooltip';
import { D3Selection } from './process-plot-d3.types';

@Component({
  selector: 'app-process-plot-d3',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <svg class="h-full w-full overflow-visible select-none" #plot></svg>
    <app-yaxis-override-dialog class="top-0 left-0" [margin]="padding"></app-yaxis-override-dialog>
  `,
})
export class ProcessPlotD3Component implements OnDestroy, AfterViewInit {
  @ViewChild('plot', {static: false}) plotElement?: ElementRef<SVGSVGElement>;
  @Input() isCollapsed = false;
  private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration).pipe(
    filter(UtilMethods.isNotNullOrUndefined));
  private processValuesLog = this.store.select(ProcessPlotSelectors.processValuesLog);
  private markedDirty = this.store.select(ProcessPlotSelectors.markedDirty);
  private scalesMarkedDirty = this.store.select(ProcessPlotSelectors.scalesMarkedDirty);
  private isZoomed = this.store.select(ProcessPlotSelectors.anySubplotZoomed);
  private xScale = scaleLinear();
  private yScales: ScaleLinear<number, number>[][] = [];
  private svg?: D3Selection<SVGSVGElement>;
  private componentDestroyed = new Subject<void>();
  private placement?: ProcessPlotD3Placement;
  private lines?: ProcessPlotD3Lines;
  private coloredRegions?: ProcessPlotD3ColoredRegions;
  private annotations?: ProcessPlotD3Annotations;
  private tooltip?: ProcessPlotD3Tooltip;
  private zoomAndPan?: ProcessPlotD3ZoomAndPan;
  private axesOverrides?: ProcessPlotD3AxesOverrides;

  constructor(private store: Store,
              private processValuePipe: ProcessValuePipe,
              private ngZone: NgZone) {}

  @HostBinding('style.padding') get padding() {
    return '1rem .5rem';
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  ngAfterViewInit() {
    this.plotConfiguration.pipe(take(1)).subscribe(plotConfiguration => {
      if(this.plotElement === undefined) return;
      this.svg = select<SVGSVGElement, unknown>(this.plotElement.nativeElement);
      this.yScales = this.createYScales(plotConfiguration);
      this.insertSvgElements(this.svg, plotConfiguration);

      this.placement = new ProcessPlotD3Placement(this.svg, this.xScale, this.yScales);
      this.lines = new ProcessPlotD3Lines(this.svg, this.xScale, this.yScales);
      this.coloredRegions = new ProcessPlotD3ColoredRegions(this.svg, this.xScale, this.yScales);
      this.annotations = new ProcessPlotD3Annotations(this.svg, this.xScale, this.yScales);
      this.tooltip = new ProcessPlotD3Tooltip(this.processValuesLog, this.processValuePipe, this.svg, this.xScale);
      this.zoomAndPan = new ProcessPlotD3ZoomAndPan(
        this.store, this.componentDestroyed, this.svg, this.xScale, this.yScales,
      );
      this.axesOverrides = new ProcessPlotD3AxesOverrides(this.store, this.svg);

      this.setupOnResize(this.plotElement.nativeElement);
      this.setupOnDataChange(plotConfiguration);
      this.setupOnPlotConfigurationChange();
      this.setupOnMarkedDirty();
      this.tooltip.setupTooltip(plotConfiguration);
      this.zoomAndPan.setupZoom(plotConfiguration);
      this.axesOverrides.setupAxesOverrides(plotConfiguration);
      this.store.dispatch(ProcessPlotActions.processPlotInitialized());
    });
  }

  private setupOnResize(element: Element) {
    const resizeObserver = new ResizeObserver((entries) => {
      // when collapsing, contentRect is 0 width and height, and errors will occur if we try placing elements.
      if(entries.some(entry => entry.contentRect.height === 0)) return;
      this.ngZone.run(() => this.store.dispatch(ProcessPlotActions.processPlotResized()));
    });
    resizeObserver.observe(element);
  }

  private createYScales(plotConfiguration: PlotConfiguration) {
    return plotConfiguration.sub_plots.map(subPlot => subPlot.axes.map(axis => {
      return scaleLinear().domain([axis.y_min, axis.y_max]);
    }));
  }

  private insertSvgElements(svg: D3Selection<SVGSVGElement>, plotConfiguration: PlotConfiguration) {
    svg.append('g').attr('class', 'x-axis');
    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = svg.append('g')
        .attr('class', `subplot subplot-${subPlotIndex}`);
      subPlotG.append('g').attr('class', 'annotations')
        .attr('fill', 'blue')
        .attr('stroke-dasharray', 1.5)
        .attr('stroke-width', 1.5)
        .style('font-size', ProcessPlotD3FontSizes.annotationLabelSize);
      plotConfiguration.color_regions.forEach((_, colorRegionIndex) => {
        subPlotG.append('g').attr('class', `color-region-${colorRegionIndex}`)
          .style('font-size', ProcessPlotD3FontSizes.annotationLabelSize)
          .attr('fill', 'black');
      });
      subPlot.axes.forEach((axis, axisIndex) => {
        subPlotG.append('g').attr('class', `x-grid-lines`).style('color', '#cccccc');
        subPlotG.append('g').attr('class', `y-grid-lines`).style('color', '#cccccc');
        subPlotG.append('rect').attr('class', `y-axis-background-${axisIndex}`)
          .attr('fill', 'white')
          .style('cursor', 'pointer');
        subPlotG.append('g').attr('class', `y-axis y-axis-${axisIndex}`)
          .style('color', axis.color)
          .style('cursor', 'pointer');
        subPlotG.append('text').attr('class', `axis-label axis-label-${axisIndex}`)
          .attr('fill', axis.color)
          .text(axis.label);
        subPlotG.append('g').attr('class', `line line-${axisIndex}`)
          .attr('clip-path', `url(#subplot-clip-path-${subPlotIndex})`)
          .attr('stroke', axis.color)
          .attr('fill', 'none')
          .attr('stroke-width', 1);
      });

      const subPlotBorderG = subPlotG.append('g').attr('class', 'subplot-border')
        .style('cursor', 'crosshair');
      subPlotBorderG.append('clipPath').attr('id', `subplot-clip-path-${subPlotIndex}`).append('rect');
      subPlotBorderG.append('rect') // actual border
        .attr('stroke-width', 1)
        .attr('stroke', 'black')
        .attr('fill', 'transparent');
      subPlotBorderG.append('line').attr('class', 'tooltip-line')
        .attr('stroke', 'black')
        .attr('stroke-width', 1.5)
        .attr('clip-path', `url(#subplot-clip-path-${subPlotIndex})`);
    });
    const tooltipG = svg.append('g').attr('class', 'tooltip')
      .style('pointer-events', 'none')
      .style('font', `${ProcessPlotD3FontSizes.tooltip}px sans-serif`);
    tooltipG.append('rect').attr('class', 'background')
      .attr('fill', 'white')
      .attr('stroke', 'gray')
      .attr('stroke-width', 1)
      .style('filter', 'drop-shadow(3px 3px 4px #8888)')
      .attr('rx', 5)
      .attr('ry', 5);
    tooltipG.append('text')
      .attr('dominant-baseline', 'hanging');
  }

  private setupOnDataChange(plotConfiguration: PlotConfiguration) {
    this.processValuesLog.pipe(
      concatLatestFrom(() => this.store.select(ProcessPlotSelectors.anySubplotZoomed)),
      takeUntil(this.componentDestroyed),
    ).subscribe(async ([processValuesLog, isZoomed]) => {
      if(isZoomed) return;
      await this.plotData(plotConfiguration, processValuesLog);
      this.updatePlacementsOnNewTopLabel(plotConfiguration, processValuesLog);
    });
  }

  private updatePlacementsOnNewTopLabel(plotConfiguration: PlotConfiguration,
                                        processValuesLog: ProcessValueLog) {
    const processValueNamesToConsider = plotConfiguration.process_value_names_to_annotate
      .concat(plotConfiguration.color_regions.map(colorRegion => colorRegion.process_value_name));

    const hasNewValue = processValueNamesToConsider.map(processValueName => {
      const colorRegionData = processValuesLog[processValueName];
      if(colorRegionData === undefined) return;
      const newestValue = colorRegionData[colorRegionData.length - 1].value;
      const olderValues = colorRegionData.slice(0, colorRegionData.length - 1).map(value => value.value);
      return !olderValues.includes(newestValue);
    }).some(value => value);

    if(hasNewValue) {
      // new color region value, label height could therefore have changed, so update placement of elements and re-plot;
      this.store.dispatch(ProcessPlotActions.newAnnotatedValueAppeared());
    }
  }

  private async plotData(plotConfiguration: PlotConfiguration,
                         processValuesLog: ProcessValueLog) {
    if(this.svg === undefined) throw Error('no Svg selection when plotting data!');
    if(!await firstValueFrom(this.isZoomed)) this.fitXScaleToData(plotConfiguration, processValuesLog);
    this.drawXAxis(plotConfiguration);
    this.lines?.plotLines(plotConfiguration, processValuesLog);
    this.coloredRegions?.plotColoredRegions(plotConfiguration, processValuesLog);
    this.annotations?.plotAnnotations(plotConfiguration, processValuesLog);
    this.tooltip?.updateLineXPosition();
  }

  private fitXScaleToData(plotConfiguration: PlotConfiguration, processValuesLog: ProcessValueLog) {
    const xAxisProcessValues = processValuesLog[plotConfiguration.x_axis_process_value_name];
    if(xAxisProcessValues === undefined) return;
    const minXValue = xAxisProcessValues.at(0)?.value ?? 0;
    const maxXValue = xAxisProcessValues.at(-1)?.value ?? minXValue;
    if(typeof minXValue !== 'number' || typeof maxXValue !== 'number') throw Error('Process Value chosen for x-axis was not a number!');
    this.xScale.domain([minXValue, maxXValue]);
  }

  private drawXAxis(plotConfiguration: PlotConfiguration) {
    this.svg?.select<SVGGElement>('.x-axis').call(axisBottom(this.xScale));
    plotConfiguration.sub_plots.forEach((_, subPlotIndex) => {
      const xGridLineAxisGenerator = this.placement?.xGridLineAxisGenerators[subPlotIndex];
      if(xGridLineAxisGenerator === undefined) return;
      this.svg?.select<SVGGElement>(`.subplot-${subPlotIndex} .x-grid-lines`).call(xGridLineAxisGenerator);
    });
  }

  private setupOnMarkedDirty() {
    this.markedDirty.pipe(filter(identity),
      concatLatestFrom(() => [this.processValuesLog, this.plotConfiguration]),
      takeUntil(this.componentDestroyed),
    ).subscribe(async ([_, processValuesLog, plotConfiguration]) => {
      this.placement?.updateElementPlacements(plotConfiguration);
      await this.plotData(plotConfiguration, processValuesLog);
      this.store.dispatch(ProcessPlotActions.processPlotElementsPlaced());
    });

    this.scalesMarkedDirty.pipe(filter(identity),
      concatLatestFrom(() => [this.processValuesLog, this.plotConfiguration]),
      takeUntil(this.componentDestroyed),
    ).subscribe(async ([_, processValuesLog, plotConfiguration]) => {
      this.placement?.updateAxes(plotConfiguration);
      await this.plotData(plotConfiguration, processValuesLog);
      this.store.dispatch(ProcessPlotActions.processPlotAxesUpdated());
    });
  }

  private setupOnPlotConfigurationChange() {
    this.plotConfiguration.pipe();
  }
}
