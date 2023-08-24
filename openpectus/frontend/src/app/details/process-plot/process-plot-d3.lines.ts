import { line, ScaleLinear, Selection } from 'd3';
import { PlotAxis, PlotConfiguration } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { ProcessValueLog } from './ngrx/process-plot.reducer';
import { ProcessPlotDashArrays } from './process-plot-dash-arrays';

export class ProcessPlotD3Lines {

  plotLines(plotConfiguration: PlotConfiguration, processValuesLog: ProcessValueLog,
            svg: Selection<SVGSVGElement, unknown, null, any>, xScale: ScaleLinear<number, number>,
            yScales: ScaleLinear<number, number>[][]) {
    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      subPlot.axes.forEach((axis, axisIndex) => {
        svg.select<SVGGElement>(`.subplot-${subPlotIndex} .line-${axisIndex}`)
          .selectAll('path')
          .data(this.formatLineDataForAxis(processValuesLog, axis))
          .join('path')
          .attr('d', line()
            .x(d => xScale(d[0]))
            .y(d => yScales[subPlotIndex][axisIndex](d[1])),
          )
          .attr('stroke-dasharray', (_, index) => ProcessPlotDashArrays[index]);
      });
    });
  }

  private formatLineDataForAxis(processValuesLog: ProcessValueLog, axis: PlotAxis): [number, number][][] {
    return axis.process_value_names
      .map(processValueName => processValuesLog[processValueName])
      .filter(UtilMethods.isNotNullOrUndefined)
      .map(processValueLine => processValueLine.map(processValue => processValue.value)
        .filter(UtilMethods.isNumber)
        .map((processValueValue, index) => [index, processValueValue]),
      );
  }
}
