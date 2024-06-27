import { ScaleLinear } from 'd3';
import { PlotConfiguration } from '../../api/models/PlotConfiguration';
import { PlotLog } from '../../api/models/PlotLog';
import { Annotation, D3Selection } from './process-plot.types';

export class ProcessPlotAnnotations {
  constructor(private plotConfiguration: PlotConfiguration,
              private svg: D3Selection<SVGSVGElement>,
              private xScale: ScaleLinear<number, number>,
              private yScales: ScaleLinear<number, number>[][]) {}

  plotAnnotations(plotLog: PlotLog, xAxisProcessValueName: string) {
    const annotationData = this.formatAnnotationData(plotLog, xAxisProcessValueName);
    const topAnnotationSelection = this.svg.select<SVGGElement>(`.annotations`);
    const top = this.yScales[0][0].range()[1];
    this.plotConfiguration.sub_plots.forEach((_, subPlotIndex) => {
      const subPlotSelection = this.svg.select<SVGGElement>(`.subplot-${subPlotIndex} .annotations`);
      const subPlotTop = this.yScales[subPlotIndex][0].range()[1];
      const subPlotBottom = this.yScales[subPlotIndex][0].range()[0];

      subPlotSelection.selectAll('line')
        .data(annotationData)
        .join('line')
        .style('visibility', d => this.getVisibility(d))
        .attr('y1', subPlotTop)
        .attr('y2', subPlotBottom)
        .attr('x1', d => this.xScale(d.x))
        .attr('x2', d => this.xScale(d.x))
        .attr('stroke', 'blue');
    });

    topAnnotationSelection.selectAll('text')
      .data(annotationData)
      .join('text')
      .style('visibility', d => this.getVisibility(d))
      .text(d => d.label ?? null)
      .attr('transform', d => `translate(${[this.xScale(d.x) + 3, top - 14]}) rotate(-90)`);

    topAnnotationSelection.selectAll('path')
      .data(annotationData)
      .join('path')
      .style('visibility', d => this.getVisibility(d))
      .attr('transform', d => `translate(${[this.xScale(d.x), top]})`)
      .attr('d', 'M -6 -12 0 -9 6 -12 0 0');
  }

  private getVisibility(d: Annotation) {
    const domain = this.xScale.range();
    const mapped = this.xScale(d.x);
    const visible = domain[0] <= mapped && mapped <= domain[1];
    return visible ? 'visible' : 'hidden';
  }

  private formatAnnotationData(plotLog: PlotLog, xAxisProcessValueName: string): Annotation[] {
    const xAxisData = plotLog.entries[xAxisProcessValueName];
    return this.plotConfiguration.process_value_names_to_annotate.flatMap(processValueNameToAnnotate => {
      const processValueData = plotLog.entries[processValueNameToAnnotate]?.values;
      if(processValueData === undefined) return [];
      return processValueData.reduce<Annotation[]>((accumulator, value, currentIndex) => {
        if(typeof value.value !== 'string' && value.value !== undefined) return accumulator;
        if(accumulator.at(-1)?.label === value.value) return accumulator;
        const x = xAxisData.values[currentIndex].value;
        if(typeof x !== 'number') throw Error('x-axis value was not a number!');
        accumulator.push({x, label: value.value});
        return accumulator;
      }, []);
    });
  }
}
