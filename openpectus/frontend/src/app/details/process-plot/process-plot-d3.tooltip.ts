import { bisector, pointer, ScaleLinear, select } from 'd3';
import { firstValueFrom, Observable } from 'rxjs';
import { PlotConfiguration, ProcessValue } from '../../api';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';
import { ProcessValueLog } from './ngrx/process-plot.reducer';
import { D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3Tooltip {
  static margin = {x: 10, y: 8};
  static fontSize = 12;
  placementRelativeToMouse = {x: 2, y: 12};

  constructor(private processValueLog: Observable<ProcessValueLog>,
              private processValuePipe: ProcessValuePipe,
              private plotConfiguration: Observable<PlotConfiguration>) {}

  setupTooltip(svg: D3Selection<SVGSVGElement>, xScale: ScaleLinear<number, number>) {
    const tooltip = svg.select<SVGGElement>('.tooltip');
    const subplotBorders = svg.selectAll('.subplot-border');
    let eventTargetParentElement: D3Selection<SVGGElement>;
    subplotBorders.on('mousemove', async (event: MouseEvent) => {
      if(event === undefined) return;
      const processValueLog = await firstValueFrom(this.processValueLog);
      const plotConfiguration = await firstValueFrom(this.plotConfiguration);
      const subplotBorderG = (event.target as SVGRectElement).parentNode as SVGGElement;
      const subplotIndex = parseInt(/subplot-(\d+)/.exec(subplotBorderG.parentElement?.classList.toString() ?? '')?.[1] ?? '');
      const subplotProcessValueNames = plotConfiguration.sub_plots[subplotIndex].axes.flatMap(axis => axis.process_value_names);
      const subplotData = Object.values(processValueLog).filter(processValues => subplotProcessValueNames.includes(processValues[0].name));
      const xAxisData = processValueLog[plotConfiguration.x_axis_process_value_name];
      const relativeMousePosition = pointer(event);
      const bisectedIndex = this.bisectX(xAxisData, xScale, relativeMousePosition[0]);
      if(bisectedIndex === undefined) return;
      const bisectedData = subplotData.flatMap(processValues => processValues[bisectedIndex]);

      tooltip.attr('transform', `translate(${[
        relativeMousePosition[0] + this.placementRelativeToMouse.x,
        relativeMousePosition[1] + this.placementRelativeToMouse.y,
      ]})`)
        .call(this.callout.bind(this), bisectedData, plotConfiguration);
      eventTargetParentElement = select(subplotBorderG);
      eventTargetParentElement.call(this.line.bind(this), xScale, xAxisData[bisectedIndex]);
    });

    subplotBorders.on('mouseleave', () => {
      tooltip.call(this.callout.bind(this));
      eventTargetParentElement.call(this.line.bind(this), xScale);
    });
  }

  private bisectX(xAxisData: ProcessValue[], xScale: ScaleLinear<number, number>, mouseX: number): number | undefined {
    if(xAxisData.length === 0) return;
    const xValue = xScale.invert(mouseX);
    return bisector((d: ProcessValue) => d.value).center(xAxisData, xValue);
  }

  private callout(tooltipG: D3Selection<SVGGElement>, processValues?: ProcessValue[], plotConfiguration?: PlotConfiguration) {
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
        .attr('y', (_, i) => `${i * ProcessPlotD3Tooltip.fontSize}pt`)
        .attr('fill', d => plotConfiguration?.sub_plots.flatMap<string | undefined>(subPlot => {
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

  private line(subPlotBorder: D3Selection<SVGGElement>, xScale: ScaleLinear<number, number>, xAxisDatum?: ProcessValue) {
    const lineSelection = subPlotBorder.selectAll('line');
    if(xAxisDatum === undefined) {
      lineSelection.style('display', 'none');
      return;
    }
    lineSelection.style('display', null);
    const rectBBox = subPlotBorder.selectChild<SVGRectElement>('rect').node()?.getBBox();
    lineSelection.data([xAxisDatum])
      .join('line')
      .attr('x1', d => xScale(d.value as number))
      .attr('x2', d => xScale(d.value as number))
      .attr('y1', rectBBox?.y ?? 0)
      .attr('y2', (rectBBox?.y ?? 0) + (rectBBox?.height ?? 0));
  }
}
