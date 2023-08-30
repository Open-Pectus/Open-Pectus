import { Store } from '@ngrx/store';
import { path, ScaleLinear } from 'd3';
import { PlotConfiguration } from '../../api';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3Zoom {
  constructor(private store: Store) {}

  setupZoom(svg: D3Selection<SVGSVGElement>,
            plotConfiguration: PlotConfiguration,
            xScale: ScaleLinear<number, number>,
            yScales: ScaleLinear<number, number>[][]) {
    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = svg.select<SVGGElement>(`g.subplot-${subPlotIndex}`);
      subPlotG.on('mousedown', this.getMouseDown(svg, subPlotG, xScale, yScales[subPlotIndex]));
      subPlotG.on('dblclick', this.getDblClick(svg));
    });
  }

  private getMouseDown(svg: D3Selection<SVGSVGElement>,
                       subPlotG: D3Selection<SVGGElement>,
                       xScale: ScaleLinear<number, number>,
                       yScales: ScaleLinear<number, number>[]) {
    return (event: MouseEvent) => {
      let path = svg.selectAll<SVGPathElement, MouseEvent>('path.zoom');
      path = path
        .data([event])
        .join('path')
        .attr('class', 'zoom')
        .attr('stroke', 'black')
        .attr('fill', 'none');
      svg.on('mousemove', this.getMouseMove(path));
      svg.on('mouseup', this.getMouseUp(svg, path, subPlotG, xScale, yScales));
    };
  }

  private getMouseMove(pathElement: D3Selection<SVGPathElement, MouseEvent>) {
    return (event: MouseEvent) => {
      pathElement.attr('d', d => {
        const pathConstructor = path();
        pathConstructor.rect(d.offsetX, d.offsetY, event.offsetX - d.offsetX, event.offsetY - d.offsetY);
        return pathConstructor.toString();
      });
    };
  }

  private getMouseUp(svg: D3Selection<SVGSVGElement>,
                     path: D3Selection<SVGPathElement, MouseEvent>,
                     subPlotG: D3Selection<SVGGElement>,
                     xScale: ScaleLinear<number, number>,
                     yScales: ScaleLinear<number, number>[]) {
    return (event: MouseEvent) => {
      svg.on('mousemove mouseup', null);
      svg.select('path.zoom').remove();

      // TODO: modify scales
      const xs = [xScale.invert(path.datum().offsetX), xScale.invert(event.offsetX)].sort();
      if(xs[0] === xs[1]) return;
      xScale.domain(xs);
      const ys = [path.datum().offsetY, event.offsetY];
      this.store.dispatch(ProcessPlotActions.processPlotZoomed());
    };
  }

  private getDblClick(svg: D3Selection<SVGSVGElement>) {
    return (event: MouseEvent) => {
      svg.on('mousemove mouseup', null);
      svg.select('path.zoom').remove();
      this.store.dispatch(ProcessPlotActions.processPlotZoomReset());
    };
  }
}
