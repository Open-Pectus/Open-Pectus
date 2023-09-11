import { Store } from '@ngrx/store';
import { bisector, pointer, ScaleLinear, select } from 'd3';
import { firstValueFrom } from 'rxjs';
import { PlotConfiguration, ProcessValue } from '../../api';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { ProcessPlotFontSizes } from './process-plot.font-sizes';
import { D3Selection } from './process-plot.types';

export class ProcessPlotTooltip {
  static margin = {x: 10, y: 8};
  placementRelativeToMouse = {x: 1, y: 14};
  private processValuesLog = this.store.select(ProcessPlotSelectors.processValuesLog);
  private xAxisProcessValue = this.store.select(ProcessPlotSelectors.xAxisProcessValueName);

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
      const xAxisProcessValue = await firstValueFrom(this.xAxisProcessValue);
      if(xAxisProcessValue === undefined) return;

      const subplotBorderG = (event.target as SVGRectElement).parentNode as SVGGElement;
      const subplotIndex = parseInt(/subplot-(\d+)/.exec(subplotBorderG.parentElement?.classList.toString() ?? '')?.[1] ?? '');
      const subplotProcessValueNames = this.plotConfiguration.sub_plots[subplotIndex].axes.flatMap(axis => axis.process_value_names);
      const subplotData = Object.values(processValuesLog).filter(processValues => subplotProcessValueNames.includes(processValues[0].name));
      const xAxisData = processValuesLog[xAxisProcessValue];
      const relativeMousePosition = pointer(event);
      const bisectedIndex = this.bisectX(xAxisData, relativeMousePosition[0]);
      if(bisectedIndex === undefined) return;
      const bisectedData = subplotData.flatMap(processValues => processValues[bisectedIndex]);

      tooltip.attr('transform', `translate(${[
        relativeMousePosition[0] + this.placementRelativeToMouse.x,
        relativeMousePosition[1] + this.placementRelativeToMouse.y,
      ]})`)
        .call(this.callout.bind(this), bisectedData);
      eventTargetParentElement = select(subplotBorderG);
      eventTargetParentElement.call(this.line.bind(this), xAxisData[bisectedIndex]);
    });

    subplotBorders.on('mouseleave', () => {
      tooltip.call(this.callout.bind(this));
      eventTargetParentElement.call(this.line.bind(this));
    });
  }

  updateLineXPosition() {
    this.svg.selectAll('.subplot-border').selectAll<SVGLineElement, ProcessValue>('line')
      .filter(d => d !== undefined)
      .attr('x1', d => this.xScale(d.value as number))
      .attr('x2', d => this.xScale(d.value as number));
  }

  updateLineYPosition() {
    const subPlotBorders = this.svg.selectAll<SVGGElement, unknown>('.subplot-border');
    subPlotBorders.each((_, index, groups) => {
      const subPlotBorder = select(groups[index]);
      const rectBBox = subPlotBorder.selectChild<SVGRectElement>('rect').node()?.getBBox();
      subPlotBorder.selectAll<SVGLineElement, ProcessValue>('line')
        .filter(d => d !== undefined)
        .attr('y1', rectBBox?.y ?? 0)
        .attr('y2', (rectBBox?.y ?? 0) + (rectBBox?.height ?? 0));
    });
  }

  private bisectX(xAxisData: ProcessValue[], mouseX: number): number | undefined {
    if(xAxisData === undefined || xAxisData.length === 0) return;
    const xValue = this.xScale.invert(mouseX);
    return bisector((d: ProcessValue) => d.value).center(xAxisData, xValue);
  }

  private callout(tooltipG: D3Selection<SVGGElement>, processValues?: ProcessValue[]) {
    if(processValues === undefined) {
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
        .text((processValue) => {
          return `${processValue.name}: ${this.processValuePipe.transform(processValue)}`;
        }),
      );

    const textNode = text.node() as SVGTextElement;
    const {width, height} = textNode.getBBox();
    tooltipG.selectChild('rect.background')
      .attr('width', width + 2 * ProcessPlotTooltip.margin.x)
      .attr('height', height + 2 * ProcessPlotTooltip.margin.y);
  }

  private line(subPlotBorder: D3Selection<SVGGElement>, xAxisDatum?: ProcessValue) {
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
