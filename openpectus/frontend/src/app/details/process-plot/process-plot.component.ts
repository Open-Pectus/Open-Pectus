import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, HostBinding, OnDestroy, ViewChild } from '@angular/core';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { axisBottom, ScaleLinear, scaleLinear, select } from 'd3';
import { combineLatest, filter, identity, Subject, take, takeUntil } from 'rxjs';
import { PlotConfiguration } from '../../api/models/PlotConfiguration';
import { PlotLog } from '../../api/models/PlotLog';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';
import { UtilMethods } from '../../shared/util-methods';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { ProcessPlotAnnotations } from './process-plot.annotations';
import { ProcessPlotAxesOverrides } from './process-plot.axes-overrides';
import { ProcessPlotColoredRegions } from './process-plot.colored-regions';
import { ProcessPlotFontSizes } from './process-plot.font-sizes';
import { ProcessPlotLines } from './process-plot.lines';
import { ProcessPlotPlacement } from './process-plot.placement';
import { ProcessPlotTooltip } from './process-plot.tooltip';
import { D3Selection } from './process-plot.types';
import { ProcessPlotZoomAndPan } from './process-plot.zoom-and-pan';
import { XAxisOverrideDialogComponent } from './x-axis-override-dialog.component';
import { YAxisOverrideDialogComponent } from './y-axis-override-dialog.component';

@Component({
  selector: 'app-process-plot',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [YAxisOverrideDialogComponent, XAxisOverrideDialogComponent],
  template: `
    <svg class="h-full w-full overflow-visible select-none" #plot></svg>
    <app-y-axis-override-dialog class="top-0 left-0" [margin]="padding"></app-y-axis-override-dialog>
    <app-x-axis-override-dialog class="top-0 left-0" [margin]="padding"></app-x-axis-override-dialog>
  `,
})
export class ProcessPlotComponent implements OnDestroy, AfterViewInit {
  @ViewChild('plot', {static: false}) plotElement?: ElementRef<SVGSVGElement>;
  @HostBinding('style.padding') readonly padding = '1rem .5rem';
  private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration).pipe(
    filter(UtilMethods.isNotNullOrUndefined));
  private plotLog = this.store.select(ProcessPlotSelectors.plotLog);
  private markedDirty = this.store.select(ProcessPlotSelectors.markedDirty);
  private anySubplotZoomed = this.store.select(ProcessPlotSelectors.anySubplotZoomed);
  private yAxesLimitsOverride = this.store.select(ProcessPlotSelectors.yAxesLimitsOverride);
  private zoomAndPanDomainOverrides = this.store.select(ProcessPlotSelectors.zoomAndPanDomainOverrides);
  private xAxisProcessValueName = this.store.select(ProcessPlotSelectors.xAxisProcessValueName).pipe(
    filter(UtilMethods.isNotNullOrUndefined));
  private xScale = scaleLinear();
  private yScales: ScaleLinear<number, number>[][] = [];
  private svg?: D3Selection<SVGSVGElement>;
  private componentDestroyed = new Subject<void>();
  private placement?: ProcessPlotPlacement;
  private lines?: ProcessPlotLines;
  private coloredRegions?: ProcessPlotColoredRegions;
  private annotations?: ProcessPlotAnnotations;
  private tooltip?: ProcessPlotTooltip;
  private zoomAndPan?: ProcessPlotZoomAndPan;
  private axesOverrides?: ProcessPlotAxesOverrides;

  constructor(private store: Store,
              private processValuePipe: ProcessValuePipe) {}

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  ngAfterViewInit() {
    this.plotConfiguration.pipe(take(1)).subscribe(plotConfiguration => {
      if(this.plotElement === undefined) return;
      this.svg = select<SVGSVGElement, unknown>(this.plotElement.nativeElement);
      this.yScales = this.createYScales(plotConfiguration);
      this.insertSvgElements(plotConfiguration, this.svg);

      this.placement = new ProcessPlotPlacement(plotConfiguration, this.svg, this.xScale, this.yScales);
      this.lines = new ProcessPlotLines(plotConfiguration, this.svg, this.xScale, this.yScales);
      this.coloredRegions = new ProcessPlotColoredRegions(plotConfiguration, this.svg, this.xScale, this.yScales);
      this.annotations = new ProcessPlotAnnotations(plotConfiguration, this.svg, this.xScale, this.yScales);
      this.tooltip = new ProcessPlotTooltip(this.store, plotConfiguration, this.processValuePipe, this.svg, this.xScale);
      this.zoomAndPan = new ProcessPlotZoomAndPan(
        this.store, this.componentDestroyed, plotConfiguration, this.svg, this.xScale, this.yScales,
      );
      this.axesOverrides = new ProcessPlotAxesOverrides(this.store, plotConfiguration, this.svg);

      this.setupOnResize(this.plotElement.nativeElement);
      this.setupOnDataChange(plotConfiguration);
      this.setupOnAxesConfigurationChange(this.svg);
      this.setupOnMarkedDirty();
      this.tooltip.setupTooltip();
      this.zoomAndPan.setupZoom();
      this.axesOverrides.setupAxesOverrides();
      this.store.dispatch(ProcessPlotActions.processPlotInitialized());
    });
  }

  private setupOnResize(element: Element) {
    const resizeObserver = new ResizeObserver((entries) => {
      // when collapsing, contentRect is 0 width and height, and errors will occur if we try placing elements.
      if(entries.some(entry => entry.contentRect.height === 0)) return;
      this.store.dispatch(ProcessPlotActions.processPlotResized());
    });
    resizeObserver.observe(element);
  }

  private createYScales(plotConfiguration: PlotConfiguration) {
    return plotConfiguration.sub_plots.map(subPlot => subPlot.axes.map(axis => {
      return scaleLinear().domain([axis.y_min, axis.y_max]);
    }));
  }

  private insertSvgElements(plotConfiguration: PlotConfiguration, svg: D3Selection<SVGSVGElement>) {
    svg.append('rect').attr('class', `x-axis-background`)
      .attr('fill', 'white')
      .style('cursor', 'pointer');
    svg.append('g').attr('class', 'x-axis')
      .style('cursor', 'pointer');
    svg.append('text').attr('class', 'x-axis-label')
      .style('cursor', 'pointer')
      .attr('font-size', ProcessPlotFontSizes.axisLabelSize);
    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = svg.append('g')
        .attr('class', `subplot subplot-${subPlotIndex}`);
      subPlotG.append('g').attr('class', 'annotations')
        .attr('fill', 'blue')
        .attr('stroke-dasharray', 1.5)
        .attr('stroke-width', 1.5)
        .style('font-size', ProcessPlotFontSizes.annotationLabelSize);
      plotConfiguration.color_regions.forEach((_, colorRegionIndex) => {
        subPlotG.append('g').attr('class', `color-region-${colorRegionIndex}`)
          .style('font-size', ProcessPlotFontSizes.annotationLabelSize)
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
        subPlotG.append('text').attr('class', `y-axis-label y-axis-label-${axisIndex}`)
          .attr('fill', axis.color)
          .style('cursor', 'pointer')
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
      .style('font', `${ProcessPlotFontSizes.tooltip}px sans-serif`);
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
    this.plotLog.pipe(
      concatLatestFrom(() => [
        this.anySubplotZoomed,
        this.xAxisProcessValueName,
      ]),
      takeUntil(this.componentDestroyed),
    ).subscribe(async ([processValuesLog, isZoomed, xAxisProcessValueName]) => {
      if(isZoomed) return;
      this.fitXScaleToData(processValuesLog, xAxisProcessValueName);
      this.plotData(plotConfiguration, processValuesLog, xAxisProcessValueName);
      this.updatePlacementsOnNewTopLabel(plotConfiguration, processValuesLog);
    });
  }

  private updatePlacementsOnNewTopLabel(plotConfiguration: PlotConfiguration,
                                        plotLog: PlotLog) {
    const processValueNamesToConsider = plotConfiguration.process_value_names_to_annotate
      .concat(plotConfiguration.color_regions.map(colorRegion => colorRegion.process_value_name));

    const hasNewValue = processValueNamesToConsider.map(processValueName => {
      const colorRegionData = plotLog.entries[processValueName]?.values;
      if(colorRegionData === undefined || colorRegionData.length === 0) return;
      const newestValue = colorRegionData[colorRegionData.length - 1].value;
      const olderValues = colorRegionData.slice(0, colorRegionData.length - 1).map(value => value.value);
      return !olderValues.includes(newestValue);
    }).some(value => value);

    if(hasNewValue) {
      // new color region value, label height could therefore have changed, so update placement of elements and re-plot;
      this.store.dispatch(ProcessPlotActions.newAnnotatedValueAppeared());
    }
  }

  private plotData(plotConfiguration: PlotConfiguration,
                   plotLog: PlotLog,
                   xAxisProcessValueName: string) {
    if(this.svg === undefined) throw Error('no Svg selection when plotting data!');
    this.drawXAxis(plotConfiguration);
    this.lines?.plotLines(plotLog, xAxisProcessValueName);
    this.coloredRegions?.plotColoredRegions(plotLog, xAxisProcessValueName);
    this.annotations?.plotAnnotations(plotLog, xAxisProcessValueName);
    this.tooltip?.updateLineXPosition();
  }

  private fitXScaleToData(plotLog: PlotLog, xAxisProcessValueName: string) {
    const xAxisProcessValues = plotLog.entries[xAxisProcessValueName]?.values;
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
      concatLatestFrom(() => [
        this.plotLog,
        this.plotConfiguration,
        this.xAxisProcessValueName,
      ]),
      takeUntil(this.componentDestroyed),
    ).subscribe(async ([_, processValuesLog, plotConfiguration, xAxisProcessValueName]) => {
      this.placement?.updateElementPlacements();
      this.tooltip?.updateLineYPosition();
      this.plotData(plotConfiguration, processValuesLog, xAxisProcessValueName);
      this.store.dispatch(ProcessPlotActions.processPlotElementsPlaced());
    });
  }

  private setupOnAxesConfigurationChange(svg: D3Selection<SVGSVGElement>) {
    combineLatest([
      this.yAxesLimitsOverride,
      this.zoomAndPanDomainOverrides,
      this.xAxisProcessValueName,
    ]).pipe(
      concatLatestFrom(() => [this.plotLog, this.plotConfiguration]),
      takeUntil(this.componentDestroyed),
    ).subscribe(async ([[yAxesLimitsOverride, zoomAndPanDomainOverrides, xAxisProcessValueName], processValuesLog, plotConfiguration]) => {
      plotConfiguration.sub_plots.forEach((subPlotConfig, subPlotIndex) => {
        subPlotConfig.axes.forEach((axisConfig, axisIndex) => {
          this.yScales[subPlotIndex][axisIndex].domain([axisConfig.y_min, axisConfig.y_max]);
        });
      });

      yAxesLimitsOverride?.forEach((subPlotConfig, subPlotIndex) => {
        subPlotConfig.forEach((axisConfig, axisIndex) => {
          if(axisConfig === null) return;
          this.yScales[subPlotIndex][axisIndex].domain([axisConfig.min, axisConfig.max]);
        });
      });

      svg.select('text.x-axis-label').text(xAxisProcessValueName);
      this.fitXScaleToData(processValuesLog, xAxisProcessValueName);
      if(zoomAndPanDomainOverrides !== undefined) {
        zoomAndPanDomainOverrides.y.forEach((subPlotConfig, subPlotIndex) => {
          subPlotConfig.forEach((axisConfig, axisIndex) => {
            if(axisConfig === null) return;
            this.yScales[subPlotIndex][axisIndex].domain([axisConfig.min, axisConfig.max]);
          });
        });
        this.xScale.domain([zoomAndPanDomainOverrides.x.min, zoomAndPanDomainOverrides.x.max]);
      }
      this.placement?.updateAxes();
      this.plotData(plotConfiguration, processValuesLog, xAxisProcessValueName);
    });
  }
}
