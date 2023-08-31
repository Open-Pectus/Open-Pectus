import { Store } from '@ngrx/store';
import { path, ScaleLinear } from 'd3';
import { firstValueFrom, Subject, takeUntil } from 'rxjs';
import { PlotConfiguration } from '../../api';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3ZoomAndPan {
  private zoomedSubplotIndices = this.store.select(ProcessPlotSelectors.zoomedSubplotIndices);

  constructor(private store: Store, private componentDestroyed: Subject<void>) {}

  setupZoom(svg: D3Selection<SVGSVGElement>,
            plotConfiguration: PlotConfiguration,
            xScale: ScaleLinear<number, number>,
            yScales: ScaleLinear<number, number>[][]) {
    plotConfiguration.sub_plots.forEach((_, subPlotIndex) => {
      const subPlotG = svg.select<SVGGElement>(`g.subplot-${subPlotIndex}`);
      subPlotG.on('mousedown', this.getMouseDown(svg, xScale, yScales, subPlotIndex));
      subPlotG.on('dblclick', this.getDblClick(svg, plotConfiguration, yScales));
    });

    this.zoomedSubplotIndices.pipe(takeUntil(this.componentDestroyed)).subscribe((zoomedSubplotIndices) => {
      plotConfiguration.sub_plots.forEach((_, subPlotIndex) => {
        const isZoomed = zoomedSubplotIndices.includes(subPlotIndex);
        const cursor = isZoomed ? 'grab' : 'auto';
        this.setSubplotCursor(svg, subPlotIndex, cursor);
      });
    });
  }

  private clearSubplotCursor(svg: D3Selection<SVGSVGElement>) {
    svg.selectAll('.subplot').selectAll('.subplot-border').style('cursor', null);
  }

  private setSubplotCursor(svg: D3Selection<SVGSVGElement>, subPlotIndex: number, cursor: string) {
    svg.select(`.subplot-${subPlotIndex}`).selectChild('.subplot-border').style('cursor', cursor);
  }

  private getMouseDown(svg: D3Selection<SVGSVGElement>,
                       xScale: ScaleLinear<number, number>,
                       yScales: ScaleLinear<number, number>[][],
                       subPlotIndex: number) {
    return async (mouseDownEvent: MouseEvent) => {
      const subPlotIsAlreadyZoomed = (await firstValueFrom(this.zoomedSubplotIndices)).includes(subPlotIndex);
      if(subPlotIsAlreadyZoomed) {
        this.startDragToPan(svg, xScale, yScales, subPlotIndex);
      } else {
        this.startDragToZoom(svg, mouseDownEvent, xScale, yScales, subPlotIndex);
      }
    };
  }

  private startDragToZoom(svg: D3Selection<SVGSVGElement>,
                          mouseDownEvent: MouseEvent,
                          xScale: ScaleLinear<number, number>,
                          yScales: ScaleLinear<number, number>[][],
                          subPlotIndex: number) {
    let path = svg.selectAll<SVGPathElement, MouseEvent>('path.zoom');
    path = path
      .data([mouseDownEvent])
      .join('path').attr('class', 'zoom')
      .attr('pointer-events', 'none')
      .attr('stroke', 'black')
      .attr('fill', 'none');
    svg.on('mousemove', this.getMouseMoveForDragToZoom(path));
    svg.on('mouseup', this.getMouseUpForDragToZoom(svg, path, xScale, yScales, subPlotIndex));
  }

  private getMouseMoveForDragToZoom(pathSelection: D3Selection<SVGPathElement, MouseEvent>) {
    return (mouseMoveEvent: MouseEvent) => {
      pathSelection.attr('d', d => {
        const pathConstructor = path();
        pathConstructor.rect(d.offsetX, d.offsetY, mouseMoveEvent.offsetX - d.offsetX, mouseMoveEvent.offsetY - d.offsetY);
        return pathConstructor.toString();
      });
    };
  }

  private getMouseUpForDragToZoom(svg: D3Selection<SVGSVGElement>,
                                  pathSelection: D3Selection<SVGPathElement, MouseEvent>,
                                  xScale: ScaleLinear<number, number>,
                                  yScales: ScaleLinear<number, number>[][],
                                  subPlotIndex: number) {
    return (mouseUpEvent: MouseEvent) => {
      svg.on('mousemove mouseup', null);
      svg.select('path.zoom').remove();

      const xs = [pathSelection.datum().offsetX, mouseUpEvent.offsetX]
        .sort((a, b) => a - b)
        .map(offset => xScale.invert(offset));
      if(xs[0] === xs[1]) return; // protection from zooming to a single point on mouse click.
      xScale.domain(xs);

      yScales[subPlotIndex].forEach((yScale) => {
        const ys = [pathSelection.datum().offsetY, mouseUpEvent.offsetY]
          .sort((a, b) => a - b)
          .map(offset => yScale.invert(offset));
        yScale.domain([ys[1], ys[0]]);
      });

      this.store.dispatch(ProcessPlotActions.processPlotZoomed({subPlotIndex}));
    };
  }

  private getDblClick(svg: D3Selection<SVGSVGElement>,
                      plotConfiguration: PlotConfiguration,
                      yScales: ScaleLinear<number, number>[][]) {
    return (_: MouseEvent) => {
      this.clearSubplotCursor(svg);
      svg.on('mousemove mouseup', null);
      svg.select('path.zoom').remove();
      plotConfiguration.sub_plots.map((subPlot, subPlotIndex) => subPlot.axes.map((axis, axisIndex) => {
        yScales[subPlotIndex][axisIndex].domain([axis.y_min, axis.y_max]);
      }));
      this.store.dispatch(ProcessPlotActions.processPlotZoomReset());
    };
  }

  private startDragToPan(svg: D3Selection<SVGSVGElement>,
                         xScale: ScaleLinear<number, number>,
                         yScales: ScaleLinear<number, number>[][],
                         subPlotIndex: number) {
    this.setSubplotCursor(svg, subPlotIndex, 'grabbing');
    svg.on('mousemove', this.getMouseMoveForDragToPan(xScale, yScales, subPlotIndex));
    svg.on('mouseup', this.getMouseUpForDragToPan(svg, subPlotIndex));
  }

  private getMouseMoveForDragToPan(xScale: ScaleLinear<number, number>,
                                   yScales: ScaleLinear<number, number>[][],
                                   subPlotIndex: number) {
    return (mouseEvent: MouseEvent) => {
      this.scaleDomainFromMovement(xScale, mouseEvent.movementX);
      yScales[subPlotIndex].forEach(yScale => this.scaleDomainFromMovement(yScale, mouseEvent.movementY));
      this.store.dispatch(ProcessPlotActions.processPlotPanned());
    };
  }

  private scaleDomainFromMovement(scale: ScaleLinear<number, number>, movement: number) {
    const domain = scale.domain();
    const domainZero = scale.invert(0);
    const domainMovement = scale.invert(movement) - domainZero;
    scale.domain([domain[0] - domainMovement, domain[1] - domainMovement]);
  }

  private getMouseUpForDragToPan(svg: D3Selection<SVGSVGElement>, subPlotIndex: number) {
    return (_: MouseEvent) => {
      this.setSubplotCursor(svg, subPlotIndex, 'grab');
      svg.on('mousemove mouseup', null);
    };
  }
}
