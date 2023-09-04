import { bisector, pointer, ScaleLinear, select } from 'd3';
import { firstValueFrom, Observable } from 'rxjs';
import { PlotConfiguration, ProcessValue } from '../../api';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';
import { ProcessValueLog } from './ngrx/process-plot.reducer';
import { ProcessPlotD3FontSizes } from './process-plot-d3.font-sizes';
import { D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3Tooltip {
  static margin = {x: 10, y: 8};
  placementRelativeToMouse = {x: 1, y: 14};

  constructor(private processValueLog: Observable<ProcessValueLog>,
              private processValuePipe: ProcessValuePipe,
              private plotConfiguration: PlotConfiguration,
              private svg: D3Selection<SVGSVGElement>,
              private xScale: ScaleLinear<number, number>) {}

  setupTooltip() {
    const tooltip = this.svg.select<SVGGElement>('.tooltip');
    const subplotBorders = this.svg.selectAll('.subplot-border');
    let eventTargetParentElement: D3Selection<SVGGElement>;
    subplotBorders.on('mousemove', async (event: MouseEvent) => {
      if(event === undefined) return;
      const processValueLog = await firstValueFrom(this.processValueLog);
      const subplotBorderG = (event.target as SVGRectElement).parentNode as SVGGElement;
      const subplotIndex = parseInt(/subplot-(\d+)/.exec(subplotBorderG.parentElement?.classList.toString() ?? '')?.[1] ?? '');
      const subplotProcessValueNames = this.plotConfiguration.sub_plots[subplotIndex].axes.flatMap(axis => axis.process_value_names);
      const subplotData = Object.values(processValueLog).filter(processValues => subplotProcessValueNames.includes(processValues[0].name));
      const xAxisData = processValueLog[this.plotConfiguration.x_axis_process_value_name];
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

  private bisectX(xAxisData: ProcessValue[], mouseX: number): number | undefined {
    if(xAxisData.length === 0) return;
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
      .attr('transform', `translate(${[ProcessPlotD3Tooltip.margin.x, ProcessPlotD3Tooltip.margin.y + 2]})`)
      .call(txt => txt
        .selectAll('tspan')
        .data(processValues)
        .join('tspan')
        .attr('x', 0)
        .attr('y', (_, i) => `${i * ProcessPlotD3FontSizes.tooltip}pt`)
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
      .attr('width', width + 2 * ProcessPlotD3Tooltip.margin.x)
      .attr('height', height + 2 * ProcessPlotD3Tooltip.margin.y);
  }

  private line(subPlotBorder: D3Selection<SVGGElement>, xAxisDatum?: ProcessValue) {
    const lineSelection = subPlotBorder.selectAll('line');
    if(xAxisDatum === undefined) {
      lineSelection.style('display', 'none');
      return;
    }
    lineSelection.style('display', null);
    const rectBBox = subPlotBorder.selectChild<SVGRectElement>('rect').node()?.getBBox();
    lineSelection.data([xAxisDatum])
      .join('line')
      .attr('x1', d => this.xScale(d.value as number))
      .attr('x2', d => this.xScale(d.value as number))
      .attr('y1', rectBBox?.y ?? 0)
      .attr('y2', (rectBBox?.y ?? 0) + (rectBBox?.height ?? 0));
  }
}
