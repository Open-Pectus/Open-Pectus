import { Store } from '@ngrx/store';
import { path, ScaleLinear } from 'd3';
import { PlotConfiguration } from '../../api';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotD3Placement } from './process-plot-d3.placement';
import { D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3Zoom {
  constructor(private store: Store, private placement: ProcessPlotD3Placement) {}

  setupZoom(svg: D3Selection<SVGSVGElement>,
            plotConfiguration: PlotConfiguration,
            xScale: ScaleLinear<number, number>,
            yScales: ScaleLinear<number, number>[][]) {
    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = svg.select<SVGGElement>(`g.subplot-${subPlotIndex}`);
      subPlotG.on('mousedown', this.getMouseDown(svg, xScale, yScales, subPlotIndex, plotConfiguration));
      subPlotG.on('dblclick', this.getDblClick(svg, plotConfiguration, xScale, yScales));
    });
  }

  private getMouseDown(svg: D3Selection<SVGSVGElement>,
                       xScale: ScaleLinear<number, number>,
                       yScales: ScaleLinear<number, number>[][],
                       subPlotIndex: number,
                       plotConfiguration: PlotConfiguration) {
    return (mouseDownEvent: MouseEvent) => {
      let path = svg.selectAll<SVGPathElement, MouseEvent>('path.zoom');
      path = path
        .data([mouseDownEvent])
        .join('path')
        .attr('pointer-events', 'none')
        .attr('class', 'zoom')
        .attr('stroke', 'black')
        .attr('fill', 'none');
      svg.on('mousemove', this.getMouseMove(path));
      svg.on('mouseup', this.getMouseUp(svg, path, xScale, yScales, subPlotIndex, plotConfiguration));
    };
  }

  private getMouseMove(pathSelection: D3Selection<SVGPathElement, MouseEvent>) {
    return (mouseMoveEvent: MouseEvent) => {
      pathSelection.attr('d', d => {
        const pathConstructor = path();
        pathConstructor.rect(d.offsetX, d.offsetY, mouseMoveEvent.offsetX - d.offsetX, mouseMoveEvent.offsetY - d.offsetY);
        return pathConstructor.toString();
      });
    };
  }

  private getMouseUp(svg: D3Selection<SVGSVGElement>,
                     pathSelection: D3Selection<SVGPathElement, MouseEvent>,
                     xScale: ScaleLinear<number, number>,
                     yScales: ScaleLinear<number, number>[][],
                     subPlotIndex: number,
                     plotConfiguration: PlotConfiguration) {
    return (mouseUpEvent: MouseEvent) => {
      svg.on('mousemove mouseup', null);
      svg.select('path.zoom').remove();
      const xs = [pathSelection.datum().offsetX, mouseUpEvent.offsetX].sort((a, b) => a - b).map(
        (offset) => xScale.invert(offset - 5 /* margin, maybe needed? */));
      if(xs[0] === xs[1]) return; // protect against zooming to a single data point
      xScale.domain(xs);
      yScales[subPlotIndex].forEach((yScale) => {
        const ys = [pathSelection.datum().offsetY, mouseUpEvent.offsetY].sort((a, b) => a - b).map(
          (offset) => yScale.invert(offset - 10 /* margin, maybe needed? */));
        yScale.domain([ys[1], ys[0]]);
      });
      this.store.dispatch(ProcessPlotActions.processPlotZoomed());
      this.placement.updateElementPlacements(plotConfiguration, svg, xScale, yScales);
    };
  }

  private getDblClick(svg: D3Selection<SVGSVGElement>,
                      plotConfiguration: PlotConfiguration,
                      xScale: ScaleLinear<number, number>,
                      yScales: ScaleLinear<number, number>[][]) {
    return (_: MouseEvent) => {
      svg.on('mousemove mouseup', null);
      svg.select('path.zoom').remove();
      plotConfiguration.sub_plots.map((subPlot, subPlotIndex) => subPlot.axes.map((axis, axisIndex) => {
        yScales[subPlotIndex][axisIndex].domain([axis.y_min, axis.y_max]);
      }));
      this.store.dispatch(ProcessPlotActions.processPlotZoomReset());
      this.placement.updateElementPlacements(plotConfiguration, svg, xScale, yScales);
    };
  }
}
