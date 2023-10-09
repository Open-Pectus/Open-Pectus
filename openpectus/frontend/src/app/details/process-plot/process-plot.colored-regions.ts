import { ScaleLinear } from 'd3';
import { PlotColorRegion, PlotConfiguration, PlotLog } from '../../api';
import { ColoredRegionRect, D3Selection } from './process-plot.types';

export class ProcessPlotColoredRegions {
  constructor(private plotConfiguration: PlotConfiguration,
              private svg: D3Selection<SVGSVGElement>,
              private xScale: ScaleLinear<number, number>,
              private yScales: ScaleLinear<number, number>[][]) {}

  plotColoredRegions(plotLog: PlotLog, xAxisProcessValueName: string) {
    this.plotConfiguration.color_regions.forEach((colorRegion, colorRegionIndex) => {
      const topColorRegionSelection = this.svg.select<SVGGElement>(`.color-region-${colorRegionIndex}`);
      const formattedRectData = this.formatColoredRegionsData(plotLog, colorRegion, xAxisProcessValueName);
      const top = this.yScales[0][0].range()[1];
      this.plotConfiguration.sub_plots.forEach((_, subPlotIndex) => {
        const colorRegionSelection = this.svg.select<SVGGElement>(`.subplot-${subPlotIndex} .color-region-${colorRegionIndex}`);
        const subPlotTop = this.yScales[subPlotIndex][0].range()[1];
        const subPlotBottom = this.yScales[subPlotIndex][0].range()[0];
        if(subPlotBottom < 0) return; // while expanding, this can be temporarily negative throwing errors in console. So let's avoid that.

        // Rectangle
        colorRegionSelection.selectAll('rect')
          .data(formattedRectData)
          .join('rect')
          .attr('clip-path', `url(#subplot-clip-path-${subPlotIndex})`)
          .attr('x', d => this.xScale(d.start))
          .attr('y', subPlotTop)
          .attr('width', d => this.xScale(d.end) - this.xScale(d.start))
          .attr('height', subPlotBottom - subPlotTop)
          .attr('fill', d => d.color);
      });

      // Arrow
      topColorRegionSelection.selectAll('path')
        .data(formattedRectData)
        .join('path')
        .style('visibility', d => this.getVisibility(this.getXPosition(d)))
        .attr('transform', d => `translate(${[this.getXPosition(d), top]})`)
        .attr('d', 'M -6 -12 0 -9 6 -12 0 0');

      // Label
      topColorRegionSelection.selectAll('text')
        .data(formattedRectData)
        .join('text')
        .style('visibility', d => this.getVisibility(this.getXPosition(d)))
        .attr('transform',
          d => `translate(${[this.getXPosition(d) + 3, top - 14]}) rotate(-90)`)
        .text(d => d.value ?? '');
    });
  }

  private getXPosition(d: ColoredRegionRect) {
    const start = this.xScale(d.start);
    const end = this.xScale(d.end);
    const width = end - start;
    return start + width / 2;
  }

  private formatColoredRegionsData(plotLog: PlotLog,
                                   colorRegion: PlotColorRegion,
                                   xAxisProcessValueName: string): ColoredRegionRect[] {
    const processValueLogEntry = plotLog.entries[colorRegion.process_value_name];
    if(processValueLogEntry === undefined) return [];
    const xAxisData = plotLog.entries[xAxisProcessValueName];
    // if(xAxisData.values.some(value => typeof value.value !== 'number')) throw Error('X axis has non-number value');
    let start: number = xAxisData.values.at(0)?.value as number;
    const coloredRegionRects: ColoredRegionRect[] = [];
    for(let i = 0; i < processValueLogEntry.values.length; i++) {
      const currentValueColor = colorRegion.value_color_map[processValueLogEntry.values.at(i)?.value ?? -1];
      const previousValueColor = i === 0 ? undefined : colorRegion.value_color_map[processValueLogEntry.values[i - 1]?.value ?? -1];
      if(currentValueColor === previousValueColor) continue; // same value, just skip ahead
      const end = xAxisData.values.at(i)?.value as number;
      if(previousValueColor !== undefined) {
        coloredRegionRects.push({start, end, color: previousValueColor, value: processValueLogEntry.values[i - 1]?.value});
      }
      if(currentValueColor !== undefined) start = end;
    }
    const valueAtEnd = processValueLogEntry.values.at(-1)?.value;
    const colorAtEnd = colorRegion.value_color_map[valueAtEnd ?? -1];
    if(colorAtEnd !== undefined) { // we ran past end, but was drawing a rect, so push that into array
      const end = xAxisData.values.at(-1)?.value as number;
      coloredRegionRects.push({start, end, color: colorAtEnd, value: valueAtEnd});
    }
    return coloredRegionRects;
  }


  private getVisibility(rangeValue: number) {
    const range = this.xScale.range();
    const visible = range[0] <= rangeValue && rangeValue <= range[1];
    return visible ? 'visible' : 'hidden';
  }
}
