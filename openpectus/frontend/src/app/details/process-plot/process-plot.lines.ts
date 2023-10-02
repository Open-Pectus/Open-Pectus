import { line, ScaleLinear } from 'd3';
import { PlotAxis, PlotConfiguration, PlotLog } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { ProcessPlotDashArrays } from './process-plot.dash-arrays';
import { D3Selection } from './process-plot.types';

export class ProcessPlotLines {
  constructor(private plotConfiguration: PlotConfiguration,
              private svg: D3Selection<SVGSVGElement>,
              private xScale: ScaleLinear<number, number>,
              private yScales: ScaleLinear<number, number>[][]) {}

  plotLines(plotLog: PlotLog, xAxisProcessValueName: string) {
    this.plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      subPlot.axes.forEach((axis, axisIndex) => {
        this.svg.select<SVGGElement>(`.subplot-${subPlotIndex} .line-${axisIndex}`)
          .selectAll('path')
          .data(this.formatLineDataForAxis(plotLog, axis, xAxisProcessValueName))
          .join('path')
          .attr('d', line()
            .x(d => this.xScale(d[0]))
            .y(d => this.yScales[subPlotIndex][axisIndex](d[1])),
          )
          .attr('stroke-dasharray', (_, index) => ProcessPlotDashArrays[index]);
      });
    });
  }

  private formatLineDataForAxis(plotLog: PlotLog, axis: PlotAxis, xAxisProcessValueName: string): [number, number][][] {
    return axis.process_value_names
      .map(processValueName => plotLog.entries[processValueName]?.values)
      .filter(UtilMethods.isNotNullOrUndefined)
      .map(processValueLogEntry => processValueLogEntry.map((processValue, index) => {
          if(typeof processValue.value !== 'number') return undefined;
          const x = plotLog.entries[xAxisProcessValueName].values.at(index)?.value;
          if(typeof x !== 'number') throw Error('process value chosen for x axis with non-number values');
          return [x, processValue.value] satisfies [number, number];
        }).filter(UtilMethods.isNotNullOrUndefined),
      );
  }
}
