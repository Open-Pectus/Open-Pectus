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
  private insideMargin?: Selection<SVGGElement, unknown, null, any>;
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
      const svg = select<SVGSVGElement, unknown>(this.plotElement?.nativeElement);
      this.firstTimeSetup(svg, plotConfiguration, processValuesLog);

      this.processValuesLog.pipe(takeUntil(this.componentDestroyed)).subscribe((processValuesLog) => {
        this.xScale.domain([0, processValuesLog.length]);

        this.produceData(svg, plotConfiguration, processValuesLog);
      });
    });
  }


  produceData(svg: Selection<SVGSVGElement, unknown, null, any>,
              plotConfiguration: PlotConfiguration,
              processValuesLog: ProcessValue[][]) {
    return plotConfiguration.sub_plots.flatMap((subPlot, subPlotIndex) => {
      return subPlot.axes.flatMap((axis, axisIndex) => {
        const values = axis.process_value_names.map(name => {
          return processValuesLog
            .map(processValues => processValues.find(processValue => processValue.name === name)?.value)
            .filter(UtilMethods.isNotNullOrUndefined).filter(UtilMethods.isNumber)
            .map<[number, number]>((processValue, valueIndex) => [valueIndex, processValue]);
        });

        this.insideMargin?.selectAll('path')
          .data(values)
          .attr('d', d => {
            return line()
              .x(d => this.xScale(d[0]))
              .y(d => this.yScales[axisIndex](d[1]))
              (d);
          })
          .attr('stroke', '#333')
          .attr('stroke-width', 1)
          .attr('fill', 'none');
      });
    });
  }

  private firstTimeSetup(svg: Selection<SVGSVGElement, unknown, null, any>,
                         plotConfiguration: PlotConfiguration,
                         processValuesLog: ProcessValue[][]) {
    const height = svg.node()?.width.baseVal.value ?? 0;
    const width = svg.node()?.height.baseVal.value ?? 0;
    const margin = {left: 10, top: 10, right: 10, bottom: 10};
    const padding = 10;

    this.insideMargin = svg.append('g')
      .attr('transform', 'translate(' + [margin.left, margin.top] + ')');

    // Scales
    this.yScales = plotConfiguration.sub_plots[0].axes.map(axis => scaleLinear()
      .domain([axis.y_min, axis.y_max])
      .range([0, height]),
    );
    this.xScale.range([0, width]);

    // Axes
    this.insideMargin.append('g')
      .attr('transform', `translate(${[0, height]})`)
      .call(axisBottom(this.xScale));

    plotConfiguration.sub_plots[0].axes.forEach((axis, axisIndex) => {
      const yScale = this.yScales[axisIndex];
      const x = axisIndex === 0 ? 0 : width - margin.right;
      this.insideMargin?.append('g')
        .attr('transform', `translate(${[x, padding]})`)
        .call(axisIndex === 0 ? axisLeft(yScale) : axisRight(yScale));
    });


  }
}
