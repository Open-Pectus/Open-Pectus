import { ScaleLinear } from 'd3';
import { PlotConfiguration } from '../../api';
import { ProcessValueLog } from './ngrx/process-plot.reducer';
import { Annotation, D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3Annotations {
  plotAnnotations(plotConfiguration: PlotConfiguration, processValueLog: ProcessValueLog,
                  svg: D3Selection<SVGSVGElement>,
                  xScale: ScaleLinear<number, number>,
                  yScales: ScaleLinear<number, number>[][]) {
    const annotationData = this.formatAnnotationData(processValueLog, plotConfiguration.process_value_names_to_annotate);
    const topAnnotationSelection = svg.select<SVGGElement>(`.annotations`);
    const top = yScales[0][0].range()[1];
    plotConfiguration.sub_plots.forEach((_, subPlotIndex) => {
      const subPlotSelection = svg.select<SVGGElement>(`.subplot-${subPlotIndex} .annotations`);
      const subPlotTop = yScales[subPlotIndex][0].range()[1];
      const subPlotBottom = yScales[subPlotIndex][0].range()[0];

      subPlotSelection.selectAll('line')
        .data(annotationData)
        .join('line')
        .attr('y1', subPlotTop)
        .attr('y2', subPlotBottom)
        .attr('stroke', 'blue')
        .attr('transform', d => `translate(${[xScale(d.x), 0]})`);
    });

    topAnnotationSelection.selectAll('text')
      .data(annotationData)
      .join('text')
      .text(d => d.label ?? null)
      .attr('transform', d => `translate(${[xScale(d.x) + 3, top - 14]}) rotate(-90)`);

    topAnnotationSelection.selectAll('path')
      .data(annotationData)
      .join('path')
      .attr('transform', d => `translate(${[xScale(d.x), top]})`)
      .attr('d', 'M -6 -12 0 -9 6 -12 0 0');
  }

  private formatAnnotationData(processValueLog: ProcessValueLog, processValueNamesToAnnotate: string[]): Annotation[] {
    return processValueNamesToAnnotate.flatMap(processValueNameToAnnotate => {
      const processValueData = processValueLog[processValueNameToAnnotate];
      if(processValueData === undefined) return [];
      return processValueData.reduce<Annotation[]>((accumulator, value, index) => {
        if(typeof value.value !== 'string' && value.value !== undefined) return accumulator;
        if(accumulator.at(-1)?.label === value.value) return accumulator;
        accumulator.push({x: index, label: value.value}); // TODO: index should be some time value
        return accumulator;
      }, []);
    });
  }
}
