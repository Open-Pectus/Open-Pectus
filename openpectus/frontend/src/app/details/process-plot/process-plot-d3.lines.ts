import { line, ScaleLinear } from 'd3';
import { PlotAxis, PlotConfiguration } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { ProcessValueLog } from './ngrx/process-plot.reducer';
import { D3Selection } from './process-plot-d3.types';
import { ProcessPlotDashArrays } from './process-plot-dash-arrays';

export class ProcessPlotD3Lines {
  constructor(private plotConfiguration: PlotConfiguration,
              private svg: D3Selection<SVGSVGElement>,
              private xScale: ScaleLinear<number, number>,
              private yScales: ScaleLinear<number, number>[][]) {}

  plotLines(processValuesLog: ProcessValueLog) {
    this.plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      subPlot.axes.forEach((axis, axisIndex) => {
        this.svg.select<SVGGElement>(`.subplot-${subPlotIndex} .line-${axisIndex}`)
          .selectAll('path')
          .data(this.formatLineDataForAxis(processValuesLog, axis))
          .join('path')
          .attr('d', line()
            .x(d => this.xScale(d[0]))
            .y(d => this.yScales[subPlotIndex][axisIndex](d[1])),
          )
          .attr('stroke-dasharray', (_, index) => ProcessPlotDashArrays[index]);
      });
    });
  }

  private formatLineDataForAxis(processValuesLog: ProcessValueLog, axis: PlotAxis): [number, number][][] {
    return axis.process_value_names
      .map(processValueName => processValuesLog[processValueName])
      .filter(UtilMethods.isNotNullOrUndefined)
      .map(processValueLine => processValueLine.map((processValue, index) => {
          if(typeof processValue.value !== 'number') return undefined;
          const x = processValuesLog[this.plotConfiguration.x_axis_process_value_name][index].value;
          return [x, processValue.value] as [number, number];
        }).filter(UtilMethods.isNotNullOrUndefined),
      );
  }
}
