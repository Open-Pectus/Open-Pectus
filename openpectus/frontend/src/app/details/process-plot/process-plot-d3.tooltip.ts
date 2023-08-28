import { bisector, pointer, ScaleTime, select } from 'd3';
import { firstValueFrom, Observable } from 'rxjs';
import { PlotConfiguration, ProcessValue } from '../../api';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';
import { ProcessValueLog } from './ngrx/process-plot.reducer';
import { D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3Tooltip {
  static margin = {x: 10, y: 8};
  static fontSize = 12;

  constructor(private processValueLog: Observable<ProcessValueLog>,
              private processValuePipe: ProcessValuePipe,
              private plotConfiguration: Observable<PlotConfiguration>) {}

  setupTooltip(svg: D3Selection<SVGSVGElement>, xScale: ScaleTime<number, number>) {
    const tooltip = svg.select<SVGGElement>('.tooltip');
    const subplotBorders = svg.selectAll('.subplot-border');
    let eventTargetParentElement: D3Selection<SVGGElement>;
    subplotBorders.on('touchmove mousemove', async (event: MouseEvent) => {
      if(event === undefined) return;
      const data = await firstValueFrom(this.processValueLog);
      const plotConfiguration = await firstValueFrom(this.plotConfiguration);
      const subplotBorderG = (event.target as SVGRectElement).parentNode as SVGGElement;
      eventTargetParentElement = select(subplotBorderG);
      // TODO: is there really no better way to find the subplotIndex?
      const subplotIndex = Array.prototype.indexOf.call(subplotBorderG.parentNode?.parentNode?.children, subplotBorderG.parentNode) - 1;
      const subplotProcessValueNames = plotConfiguration.sub_plots[subplotIndex].axes.flatMap(axis => axis.process_value_names);
      const subplotData = Object.values(data).filter(processValues => subplotProcessValueNames.includes(processValues[0].name));

      const relativeMousePosition = pointer(event);
      const bisected = this.bisectX(subplotData, xScale, relativeMousePosition[0]);
      if(bisected === undefined) return;

      tooltip.attr('transform', `translate(${relativeMousePosition})`)
        .call(this.callout.bind(this), bisected, plotConfiguration);
      eventTargetParentElement.call(this.line.bind(this), xScale, bisected);
    });

    subplotBorders.on('touchend mouseleave', () => {
      tooltip.call(this.callout.bind(this));
      eventTargetParentElement.call(this.line.bind(this), xScale);
    });
  }

  private bisectX<T extends { timestamp: string }>(domainData: T[][], xScale: ScaleTime<number, number>, mouseX: number): T[] | undefined {
    if(domainData.length === 0) return;
    const xValue = xScale.invert(mouseX);
    return domainData.map(processValues => {
      const index = bisector((d: T) => new Date(d.timestamp).valueOf()).left(processValues, xValue, 1);
      const a = processValues[index - 1];
      const b = processValues[index];
      return b && (xValue.valueOf() - new Date(a.timestamp).valueOf() > new Date(b.timestamp).valueOf() - xValue.valueOf()) ? b : a;
    });
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

  private line(subPlotBorder: D3Selection<SVGGElement>, xScale: ScaleTime<number, number>, processValues?: ProcessValue[]) {
    const lineSelection = subPlotBorder.selectAll('line');
    if(processValues === undefined) {
      lineSelection.style('display', 'none');
      return;
    }
    lineSelection.style('display', null);
    const rectBBox = subPlotBorder.selectChild<SVGRectElement>('rect').node()?.getBBox();
    lineSelection.data([processValues[0]])
      .join('line')
      .attr('x1', d => xScale(new Date(d.timestamp)))
      .attr('x2', d => xScale(new Date(d.timestamp)))
      .attr('y1', rectBBox?.y ?? 0)
      .attr('y2', (rectBBox?.y ?? 0) + (rectBBox?.height ?? 0))
      .attr('stroke', 'black');
  }
}
