import { Store } from '@ngrx/store';
import { bisector, pointer, ScaleLinear, select } from 'd3';
import { firstValueFrom, identity } from 'rxjs';
import { PlotConfiguration, PlotLogEntry, PlotLogEntryValue } from '../../api';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';
import { UtilMethods } from '../../shared/util-methods';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { ProcessPlotFontSizes } from './process-plot.font-sizes';
import { D3Selection } from './process-plot.types';

export class ProcessPlotTooltip {
  static margin = {x: 10, y: 8};
  placementRelativeToMouse = {x: 1, y: 14};
  private plotLog = this.store.select(ProcessPlotSelectors.plotLog);
  private xAxisProcessValueName = this.store.select(ProcessPlotSelectors.xAxisProcessValueName);

  constructor(private store: Store,
              private plotConfiguration: PlotConfiguration,
              private processValuePipe: ProcessValuePipe,
              private svg: D3Selection<SVGSVGElement>,
              private xScale: ScaleLinear<number, number>) {}

  setupTooltip() {
    const tooltip = this.svg.select<SVGGElement>('.tooltip');
    const subplotBorders = this.svg.selectAll('.subplot-border');
    let eventTargetParentElement: D3Selection<SVGGElement>;
    subplotBorders.on('mousemove', async (event: MouseEvent) => {
      if(event === undefined) return;
      const plotLog = await firstValueFrom(this.plotLog);
      const xAxisProcessValueName = await firstValueFrom(this.xAxisProcessValueName);
      if(xAxisProcessValueName === undefined) return;

      const subplotBorderG = (event.target as SVGRectElement).parentNode as SVGGElement;
      const subplotIndex = parseInt(/subplot-(\d+)/.exec(subplotBorderG.parentElement?.classList.toString() ?? '')?.[1] ?? '');
      const subplotProcessValueNames = this.plotConfiguration.sub_plots[subplotIndex].axes.flatMap(axis => axis.process_value_names);
      const subplotProcessValueLogEntries = Object.values(plotLog.entries).filter(
        processValues => subplotProcessValueNames.includes(processValues.name));
      const xAxisProcessValueLogEntry = plotLog.entries[xAxisProcessValueName];
      if(xAxisProcessValueLogEntry === undefined) return;
      const relativeMousePosition = pointer(event);
      const xAxisValues = xAxisProcessValueLogEntry.values.map<number>(value => {
        if(typeof value.value !== 'number') throw Error('Non-number x axis value');
        return value.value;
      });
      const bisectedIndex = this.bisectX(xAxisValues, relativeMousePosition[0]);
      if(bisectedIndex === undefined) return;
      const bisectedYValues = subplotProcessValueLogEntries.flatMap(processValueLogEntry => processValueLogEntry.values[bisectedIndex]);

      tooltip.attr('transform', `translate(${[
        relativeMousePosition[0] + this.placementRelativeToMouse.x,
        relativeMousePosition[1] + this.placementRelativeToMouse.y,
      ]})`)
        .call(this.callout.bind(this), subplotProcessValueLogEntries, bisectedYValues);
      eventTargetParentElement = select(subplotBorderG);
      eventTargetParentElement.call(this.line.bind(this), xAxisValues.at(bisectedIndex));
    });

    subplotBorders.on('mouseleave', () => {
      tooltip.call(this.callout.bind(this));
      eventTargetParentElement.call(this.line.bind(this));
    });
  }

  updateLineXPosition() {
    this.svg.selectAll('.subplot-border')
      .selectAll<SVGLineElement, number>('line')
      .filter(UtilMethods.isNotNullOrUndefined)
      .attr('x1', d => this.xScale(d))
      .attr('x2', d => this.xScale(d));
  }

  updateLineYPosition() {
    const subPlotBorders = this.svg.selectAll<SVGGElement, unknown>('.subplot-border');
    subPlotBorders.each((_, index, groups) => {
      const subPlotBorder = select(groups[index]);
      const rectBBox = subPlotBorder.selectChild<SVGRectElement>('rect').node()?.getBBox();
      subPlotBorder.selectAll<SVGLineElement, PlotLogEntryValue>('line')
        .filter(UtilMethods.isNotNullOrUndefined)
        .attr('y1', rectBBox?.y ?? 0)
        .attr('y2', (rectBBox?.y ?? 0) + (rectBBox?.height ?? 0));
    });
  }

  private bisectX(xAxisValues: number[], mouseX: number): number | undefined {
    if(xAxisValues === undefined || xAxisValues.length === 0) return;
    const xValue = this.xScale.invert(mouseX);
    return bisector(identity).center(xAxisValues, xValue);
  }

  private callout(tooltipG: D3Selection<SVGGElement>, plotLogEntries?: PlotLogEntry[], bisectedValues?: PlotLogEntryValue[]) {
    if(plotLogEntries === undefined || bisectedValues === undefined) {
      tooltipG.style('display', 'none');
      return;
    }
    tooltipG.style('display', null);

    const text = tooltipG.selectChild<SVGTextElement>('text')
      .attr('transform', `translate(${[ProcessPlotTooltip.margin.x, ProcessPlotTooltip.margin.y + 2]})`)
      .call(txt => txt
        .selectAll('tspan')
        .data(plotLogEntries)
        .join('tspan')
        .attr('x', 0)
        .attr('y', (_, i) => `${i * ProcessPlotFontSizes.tooltip}pt`)
        .attr('fill', d => this.plotConfiguration.sub_plots.flatMap<string | undefined>(subPlot => {
          return subPlot.axes.find(axis => {
            return axis.process_value_names.includes(d.name);
          })?.color;
        }).find<string>((value): value is string => typeof value === 'string') ?? 'black')
        .text((plotLogEntry, index) => {
          return `${plotLogEntry.name}: ${this.processValuePipe.transform({...plotLogEntry, value: bisectedValues[index].value})}`;
        }),
      );

    const textNode = text.node();
    if(textNode === null) return;
    const {width, height} = textNode.getBBox();
    tooltipG.selectChild('rect.background')
      .attr('width', width + 2 * ProcessPlotTooltip.margin.x)
      .attr('height', height + 2 * ProcessPlotTooltip.margin.y);
  }

  private line(subPlotBorder: D3Selection<SVGGElement>, xAxisDatum?: number) {
    const lineSelection = subPlotBorder.selectAll('line.tooltip-line');
    if(xAxisDatum === undefined) {
      lineSelection.style('display', 'none');
      return;
    }
    lineSelection.style('display', null);
    lineSelection.data([xAxisDatum]).join('line');
    this.updateLineXPosition();
    this.updateLineYPosition();
  }
}
