import { ScaleLinear } from 'd3';
import { PlotConfiguration } from '../../api';
import { ProcessValueLog } from './ngrx/process-plot.reducer';
import { Annotation, D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3Annotations {
  plotAnnotations(plotConfiguration: PlotConfiguration,
                  processValueLog: ProcessValueLog,
                  svg: D3Selection<SVGSVGElement>,
                  xScale: ScaleLinear<number, number>,
                  yScales: ScaleLinear<number, number>[][]) {
    const annotationData = this.formatAnnotationData(processValueLog, plotConfiguration);
    const topAnnotationSelection = svg.select<SVGGElement>(`.annotations`);
    const top = yScales[0][0].range()[1];
    plotConfiguration.sub_plots.forEach((_, subPlotIndex) => {
      const subPlotSelection = svg.select<SVGGElement>(`.subplot-${subPlotIndex} .annotations`);
      const subPlotTop = yScales[subPlotIndex][0].range()[1];
      const subPlotBottom = yScales[subPlotIndex][0].range()[0];

      subPlotSelection.selectAll('line')
        .data(annotationData)
        .join('line')
        .style('visibility', d => this.getVisibility(xScale, d))
        .attr('y1', subPlotTop)
        .attr('y2', subPlotBottom)
        .attr('x1', d => xScale(d.x))
        .attr('x2', d => xScale(d.x))
        .attr('stroke', 'blue');
    });

    topAnnotationSelection.selectAll('text')
      .data(annotationData)
      .join('text')
      .style('visibility', d => this.getVisibility(xScale, d))
      .text(d => d.label ?? null)
      .attr('transform', d => `translate(${[xScale(d.x) + 3, top - 14]}) rotate(-90)`);

    topAnnotationSelection.selectAll('path')
      .data(annotationData)
      .join('path')
      .style('visibility', d => this.getVisibility(xScale, d))
      .attr('transform', d => `translate(${[xScale(d.x), top]})`)
      .attr('d', 'M -6 -12 0 -9 6 -12 0 0');
  }

  private getVisibility(scale: ScaleLinear<number, number>, d: Annotation) {
    const domain = scale.range();
    const mapped = scale(d.x);
    const visible = domain[0] <= mapped && mapped <= domain[1];
    return visible ? 'visible' : 'hidden';
  }

  private formatAnnotationData(processValueLog: ProcessValueLog, plotConfiguration: PlotConfiguration): Annotation[] {
    return plotConfiguration.process_value_names_to_annotate.flatMap(processValueNameToAnnotate => {
      const processValueData = processValueLog[processValueNameToAnnotate];
      const xAxisData = processValueLog[plotConfiguration.x_axis_process_value_name];
      if(processValueData === undefined) return [];
      return processValueData.reduce<Annotation[]>((accumulator, value, currentIndex) => {
        if(typeof value.value !== 'string' && value.value !== undefined) return accumulator;
        if(accumulator.at(-1)?.label === value.value) return accumulator;
        const x = xAxisData[currentIndex].value;
        if(typeof x !== 'number') throw Error('x-axis value was not a number!');
        accumulator.push({x, label: value.value});
        return accumulator;
      }, []);
    });
  }
}
