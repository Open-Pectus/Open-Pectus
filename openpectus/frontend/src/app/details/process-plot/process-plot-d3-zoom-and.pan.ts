import { Store } from '@ngrx/store';
import { path, ScaleLinear } from 'd3';
import { firstValueFrom, Subject, takeUntil } from 'rxjs';
import { PlotConfiguration } from '../../api';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3ZoomAndPan {
  private zoomedSubplotIndices = this.store.select(ProcessPlotSelectors.zoomedSubplotIndices);

  constructor(private store: Store,
              private componentDestroyed: Subject<void>,
              private plotConfiguration: PlotConfiguration,
              private svg: D3Selection<SVGSVGElement>,
              private xScale: ScaleLinear<number, number>,
              private yScales: ScaleLinear<number, number>[][]) {}

  setupZoom() {
    this.plotConfiguration.sub_plots.forEach((_, subPlotIndex) => {
      const subPlotG = this.svg.select<SVGGElement>(`g.subplot-${subPlotIndex}`);
      subPlotG.on('mousedown', this.getMouseDown(subPlotIndex));
      subPlotG.on('dblclick', this.getDblClick());
    });

    this.zoomedSubplotIndices.pipe(takeUntil(this.componentDestroyed)).subscribe((zoomedSubplotIndices) => {
      this.plotConfiguration.sub_plots.forEach((_, subPlotIndex) => {
        const isZoomed = zoomedSubplotIndices.includes(subPlotIndex);
        const cursor = isZoomed ? 'grab' : 'crosshair';
        this.setSubplotCursor(subPlotIndex, cursor);
      });
    });
  }

  private setSubplotCursor(subPlotIndex: number, cursor: string) {
    this.svg.select(`.subplot-${subPlotIndex}`).selectChild('.subplot-border').style('cursor', cursor);
  }

  private getMouseDown(subPlotIndex: number) {
    return async (mouseDownEvent: MouseEvent) => {
      const subPlotIsAlreadyZoomed = (await firstValueFrom(this.zoomedSubplotIndices)).includes(subPlotIndex);
      if(subPlotIsAlreadyZoomed) {
        this.startDragToPan(subPlotIndex);
      } else {
        this.startDragToZoom(mouseDownEvent, subPlotIndex);
      }
    };
  }

  private startDragToZoom(mouseDownEvent: MouseEvent,
                          subPlotIndex: number) {
    let path = this.svg.selectAll<SVGPathElement, MouseEvent>('path.zoom');
    path = path
      .data([mouseDownEvent])
      .join('path').attr('class', 'zoom')
      .attr('pointer-events', 'none')
      .attr('stroke', 'black')
      .attr('fill', 'none');
    this.svg.on('mousemove', this.getMouseMoveForDragToZoom(path));
    this.svg.on('mouseup', this.getMouseUpForDragToZoom(path, subPlotIndex));
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

  private getMouseUpForDragToZoom(pathSelection: D3Selection<SVGPathElement, MouseEvent>,
                                  subPlotIndex: number) {
    return (mouseUpEvent: MouseEvent) => {
      this.svg.on('mousemove mouseup', null);
      this.svg.select('path.zoom').remove();

      const xs = [pathSelection.datum().offsetX, mouseUpEvent.offsetX]
        .sort((a, b) => a - b)
        .map(offset => this.xScale.invert(offset));
      if(xs[0] === xs[1]) return; // protection from zooming to a single point on mouse click.
      this.xScale.domain(xs);

      this.yScales[subPlotIndex].forEach((yScale) => {
        const ys = [pathSelection.datum().offsetY, mouseUpEvent.offsetY]
          .sort((a, b) => a - b)
          .map(offset => yScale.invert(offset));
        yScale.domain([ys[1], ys[0]]);
      });

      this.store.dispatch(ProcessPlotActions.processPlotZoomed({subPlotIndex}));
    };
  }

  private getDblClick() {
    return (_: MouseEvent) => {
      this.svg.on('mousemove mouseup', null);
      this.svg.select('path.zoom').remove();
      this.plotConfiguration.sub_plots.map((subPlot, subPlotIndex) => subPlot.axes.map((axis, axisIndex) => {
        this.yScales[subPlotIndex][axisIndex].domain([axis.y_min, axis.y_max]);
      }));
      this.store.dispatch(ProcessPlotActions.processPlotZoomReset());
    };
  }

  private startDragToPan(subPlotIndex: number) {
    this.setSubplotCursor(subPlotIndex, 'grabbing');
    this.svg.on('mousemove', this.getMouseMoveForDragToPan(subPlotIndex));
    this.svg.on('mouseup', this.getMouseUpForDragToPan(subPlotIndex));
  }

  private getMouseMoveForDragToPan(subPlotIndex: number) {
    return (mouseEvent: MouseEvent) => {
      this.scaleDomainFromMovement(this.xScale, mouseEvent.movementX);
      this.yScales[subPlotIndex].forEach(yScale => this.scaleDomainFromMovement(yScale, mouseEvent.movementY));
      this.store.dispatch(ProcessPlotActions.processPlotPanned());
    };
  }

  private scaleDomainFromMovement(scale: ScaleLinear<number, number>, movement: number) {
    const domain = scale.domain();
    const domainZero = scale.invert(0);
    const domainMovement = scale.invert(movement) - domainZero;
    scale.domain([domain[0] - domainMovement, domain[1] - domainMovement]);
  }

  private getMouseUpForDragToPan(subPlotIndex: number) {
    return (_: MouseEvent) => {
      this.setSubplotCursor(subPlotIndex, 'grab');
      this.svg.on('mousemove mouseup', null);
    };
  }
}
