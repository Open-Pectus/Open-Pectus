import { Store } from '@ngrx/store';
import { bisector, pointer, ScaleLinear, select } from 'd3';
import { firstValueFrom, identity } from 'rxjs';
import { PlotConfiguration, ProcessValue } from '../../api';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';
import { UtilMethods } from '../../shared/util-methods';
import { ProcessValueLogEntry } from './ngrx/process-plot.reducer';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { ProcessPlotFontSizes } from './process-plot.font-sizes';
import { D3Selection } from './process-plot.types';

export class ProcessPlotTooltip {
  static margin = {x: 10, y: 8};
  placementRelativeToMouse = {x: 1, y: 14};
  private processValuesLog = this.store.select(ProcessPlotSelectors.processValuesLog);
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
      const processValuesLog = await firstValueFrom(this.processValuesLog);
      const xAxisProcessValueName = await firstValueFrom(this.xAxisProcessValueName);
      if(xAxisProcessValueName === undefined) return;

      const subplotBorderG = (event.target as SVGRectElement).parentNode as SVGGElement;
      const subplotIndex = parseInt(/subplot-(\d+)/.exec(subplotBorderG.parentElement?.classList.toString() ?? '')?.[1] ?? '');
      const subplotProcessValueNames = this.plotConfiguration.sub_plots[subplotIndex].axes.flatMap(axis => axis.process_value_names);
      const subplotProcessValueLogEntries = Object.values(processValuesLog).filter(
        processValues => subplotProcessValueNames.includes(processValues.name));
      const xAxisProcessValueLogEntry = processValuesLog[xAxisProcessValueName];
      const relativeMousePosition = pointer(event);
      const bisectedIndex = this.bisectX(xAxisProcessValueLogEntry.values, relativeMousePosition[0]);
      if(bisectedIndex === undefined) return;
      const bisectedValues = subplotProcessValueLogEntries.flatMap(processValueLogEntry => processValueLogEntry.values[bisectedIndex]);

      tooltip.attr('transform', `translate(${[
        relativeMousePosition[0] + this.placementRelativeToMouse.x,
        relativeMousePosition[1] + this.placementRelativeToMouse.y,
      ]})`)
        .call(this.callout.bind(this), subplotProcessValueLogEntries, bisectedValues);
      eventTargetParentElement = select(subplotBorderG);
      eventTargetParentElement.call(this.line.bind(this), xAxisProcessValueLogEntry.values[bisectedIndex]);
    });

    subplotBorders.on('mouseleave', () => {
      tooltip.call(this.callout.bind(this));
      eventTargetParentElement.call(this.line.bind(this));
    });
  }

  updateLineXPosition() {
    this.svg.selectAll('.subplot-border')
      .selectAll<SVGLineElement, (string | number)>('line')
      .filter(UtilMethods.isNotNullOrUndefined)
      .attr('x1', d => this.xScale(d as number))
      .attr('x2', d => this.xScale(d as number));
  }

  updateLineYPosition() {
    const subPlotBorders = this.svg.selectAll<SVGGElement, unknown>('.subplot-border');
    subPlotBorders.each((_, index, groups) => {
      const subPlotBorder = select(groups[index]);
      const rectBBox = subPlotBorder.selectChild<SVGRectElement>('rect').node()?.getBBox();
      subPlotBorder.selectAll<SVGLineElement, ProcessValue>('line')
        .filter(UtilMethods.isNotNullOrUndefined)
        .attr('y1', rectBBox?.y ?? 0)
        .attr('y2', (rectBBox?.y ?? 0) + (rectBBox?.height ?? 0));
    });
  }

  private bisectX(xAxisData: ProcessValueLogEntry['values'], mouseX: number): number | undefined {
    if(xAxisData === undefined || xAxisData.length === 0) return;
    const xValue = this.xScale.invert(mouseX);
    return bisector(identity).center(xAxisData, xValue);
  }

  private callout(tooltipG: D3Selection<SVGGElement>, processValues?: ProcessValue[], processValueValues?: ProcessValueLogEntry['values']) {
    if(processValueValues === undefined || processValues === undefined) {
      tooltipG.style('display', 'none');
      return;
    }
    tooltipG.style('display', null);

    const text = tooltipG.selectChild('text')
      .attr('transform', `translate(${[ProcessPlotTooltip.margin.x, ProcessPlotTooltip.margin.y + 2]})`)
      .call(txt => txt
        .selectAll('tspan')
        .data(processValues)
        .join('tspan')
        .attr('x', 0)
        .attr('y', (_, i) => `${i * ProcessPlotFontSizes.tooltip}pt`)
        .attr('fill', d => this.plotConfiguration.sub_plots.flatMap<string | undefined>(subPlot => {
          return subPlot.axes.find(axis => {
            return axis.process_value_names.includes(d.name);
          })?.color;
        }).find<string>((value): value is string => typeof value === 'string') ?? 'black')
        .text((processValue, index) => {
          return `${processValue.name}: ${this.processValuePipe.transform({...processValue, value: processValueValues[index]})}`;
        }),
      );

    const textNode = text.node() as SVGTextElement;
    const {width, height} = textNode.getBBox();
    tooltipG.selectChild('rect.background')
      .attr('width', width + 2 * ProcessPlotTooltip.margin.x)
      .attr('height', height + 2 * ProcessPlotTooltip.margin.y);
  }

  private line(subPlotBorder: D3Selection<SVGGElement>, xAxisDatum?: string | number) {
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
