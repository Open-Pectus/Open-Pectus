import { Store } from '@ngrx/store';
import { PlotConfiguration } from '../../api';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { D3Selection } from './process-plot-d3.types';

export class ProcessPlotD3AxesOverrides {
  constructor(private store: Store,
              private svg: D3Selection<SVGSVGElement>,
  ) {}

  setupAxesOverrides(plotConfiguration: PlotConfiguration) {
    plotConfiguration.sub_plots.forEach((subplot, subplotIndex) => {
      const subplotG = this.svg.select<SVGGElement>(`g.subplot-${subplotIndex}`);
      subplot.axes.forEach((_, axisIndex) => {
        const axisBackground = subplotG.selectChild(`.y-axis-background-${axisIndex}`);
        const axisG = subplotG.selectChild(`.y-axis-${axisIndex}`);
        const onClick = this.getOnClick(subplotIndex, axisIndex);
        axisBackground.on('click', onClick);
        axisG.on('click', onClick);
      });
    });
  }

  private getOnClick(subplotIndex: number, axisIndex: number) {
    return (mouseEvent: MouseEvent) => {
      this.store.dispatch(ProcessPlotActions.yAxisClicked({
        data: {
          subplotIndex,
          axisIndex,
          position: {
            x: mouseEvent.offsetX,
            y: mouseEvent.offsetY,
          },
        },
      }));
    };
  }
}
