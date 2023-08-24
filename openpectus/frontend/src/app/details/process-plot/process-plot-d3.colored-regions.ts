import { ScaleLinear, Selection } from 'd3';
import { PlotColorRegion, PlotConfiguration } from '../../api';
import { ProcessValueLog } from './ngrx/process-plot.reducer';

export class ProcessPlotD3ColoredRegions {
  plotColoredRegions(plotConfiguration: PlotConfiguration, processValueLog: ProcessValueLog,
                     svg: Selection<SVGSVGElement, unknown, null, any>,
                     xScale: ScaleLinear<number, number>,
                     yScales: ScaleLinear<number, number>[][]) {
    plotConfiguration.color_regions.forEach((colorRegion, colorRegionIndex) => {
      const topColorRegionSelection = svg.select<SVGGElement>(`.color-region-${colorRegionIndex}`);
      const formattedRectData = this.formatColoredRegionsData(colorRegion, processValueLog);
      const top = yScales[0][0].range()[1];
      plotConfiguration.sub_plots.forEach((_, subPlotIndex) => {
        const colorRegionSelection = svg.select<SVGGElement>(`.subplot-${subPlotIndex} .color-region-${colorRegionIndex}`);
        const subPlotTop = yScales[subPlotIndex][0].range()[1];
        const subPlotBottom = yScales[subPlotIndex][0].range()[0];
        if(subPlotBottom < 0) return; // while expanding, this can be temporarily negative throwing errors in console. So let's avoid that.

        // Rectangle
        colorRegionSelection.selectAll('rect')
          .data(formattedRectData)
          .join('rect')
          .attr('x', d => xScale(d.start))
          .attr('y', subPlotTop)
          .attr('width', d => xScale(d.end) - xScale(d.start))
          .attr('height', subPlotBottom - subPlotTop)
          .attr('fill', d => d.color);
      });

      // Arrow
      topColorRegionSelection.selectAll('path')
        .data(formattedRectData)
        .join('path')
        .attr('transform', d => `translate(${[xScale(d.end) - (xScale(d.end) - xScale(d.start)) / 2, top]})`)
        .attr('d', 'M -6 -12 0 -9 6 -12 0 0');

      // Label
      topColorRegionSelection.selectAll('text')
        .data(formattedRectData)
        .join('text')
        .attr('transform',
          d => `translate(${[xScale(d.end) - (xScale(d.end) - xScale(d.start)) / 2 + 3, top - 14]}) rotate(-90)`)
        .text(d => d.value ?? '');
    });
  }

  private formatColoredRegionsData(colorRegion: PlotColorRegion, processValueLog: ProcessValueLog): ColoredRegionRect[] {
    const processValueData = processValueLog[colorRegion.process_value_name];
    if(processValueData === undefined) return [];
    const processValueValues = processValueData.map(processValue => processValue.value);
    let start: number = 0;
    const coloredRegionRects: ColoredRegionRect[] = [];
    for(let i = 0; i < processValueValues.length; i++) {
      const currentValueColor = colorRegion.value_color_map[processValueValues[i] ?? -1];
      const previousValueColor = colorRegion.value_color_map[processValueValues[i - 1] ?? -1];
      if(currentValueColor === previousValueColor) continue; // same value, just skip ahead
      if(previousValueColor !== undefined) {
        coloredRegionRects.push({start, end: i, color: previousValueColor, value: processValueValues[i - 1]});
      }
      if(currentValueColor !== undefined) start = i;
    }
    const valueAtEnd = processValueValues[processValueData.length - 1];
    const colorAtEnd = colorRegion.value_color_map[valueAtEnd ?? -1];
    if(colorAtEnd !== undefined) { // we ran past end, but was drawing a rect, so push that into array
      coloredRegionRects.push({start, end: processValueData.length - 1, color: colorAtEnd, value: valueAtEnd});
    }
    return coloredRegionRects;
  }
}


interface ColoredRegionRect {
  start: number;
  end: number;
  color: string;
  value: string | number | undefined;
}
