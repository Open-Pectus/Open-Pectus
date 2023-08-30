import { path, ScaleLinear } from 'd3';
import { PlotConfiguration } from '../../api';
import { D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3Zoom {

  setupZoom(svg: D3Selection<SVGSVGElement>,
            plotConfiguration: PlotConfiguration,
            xScale: ScaleLinear<number, number>,
            yScales: ScaleLinear<number, number>[][]) {
    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = svg.select(`g.subplot-${subPlotIndex}`);
      subPlotG.on('mousedown', this.getMouseDown(svg));
    });
  }

  private getMouseDown(svg: D3Selection<SVGSVGElement>) {
    return (event: MouseEvent) => {
      let path = svg.selectAll<SVGPathElement, MouseEvent>('path.zoom');
      path = path
        .data([event])
        .join('path')
        .attr('class', 'zoom')
        .attr('stroke', 'black')
        .attr('fill', 'none');
      svg.on('mousemove', this.getMouseMove(path));
      svg.on('mouseup', this.getMouseUp(svg));
    };
  }

  private getMouseMove(pathElement: D3Selection<SVGPathElement, MouseEvent>) {
    return (event: MouseEvent) => {
      pathElement
        .attr('d', d => {
          const pathConstructor = path();
          pathConstructor.rect(
            d.offsetX,
            d.offsetY,
            event.offsetX - d.offsetX,
            event.offsetY - d.offsetY,
          );
          return pathConstructor.toString();
        });
    };
  }

  private getMouseUp(svg: D3Selection<SVGSVGElement>) {
    return (event: MouseEvent) => {
      svg.on('mousemove', null);
      svg.select('path.zoom').remove();
    };
  }
}
