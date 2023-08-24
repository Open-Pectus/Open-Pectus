import { bisector, pointer, ScaleTime } from 'd3';
import { firstValueFrom, Observable } from 'rxjs';
import { ProcessValue } from '../../api';
import { ProcessValueLog } from './ngrx/process-plot.reducer';
import { D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3Tooltip {
  constructor(private processValueLog: Observable<ProcessValueLog>) {}

  setupTooltip(svg: D3Selection<SVGSVGElement>, xScale: ScaleTime<number, number>) {
    const tooltip = svg.select<SVGGElement>('.tooltip');
    svg.on('touchmove mousemove', async (event: MouseEvent) => {
      if(event === undefined) return;
      const data = await firstValueFrom(this.processValueLog);
      const relativeMousePosition = pointer(event);
      const bisected = this.bisectX(Object.values(data), xScale, relativeMousePosition[0]);
      if(bisected === undefined) return;

      tooltip.attr('transform', `translate(${relativeMousePosition})`)
        .call(this.callout, bisected);
    });

    svg.on('touchend mouseleave', () => tooltip.call(this.callout));
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

  private callout(tooltipG: D3Selection<SVGGElement>, processValues?: ProcessValue[]) {
    if(processValues === undefined) {
      tooltipG.style('display', 'none');
      return;
    }
    tooltipG.style('display', null);
    tooltipG.selectAll('text')
      .data(processValues)
      .join('text')
      .attr('transform', (_, index) => `translate(${[0, index * 12]})`)
      .text((processValue) => processValue.value ?? '');
  }
}
