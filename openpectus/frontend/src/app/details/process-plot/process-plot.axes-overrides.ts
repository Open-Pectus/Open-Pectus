import { Store } from '@ngrx/store';
import { PlotConfiguration } from '../../api/models/PlotConfiguration';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { D3Selection } from './process-plot.types';

export class ProcessPlotAxesOverrides {
  constructor(private store: Store,
              private plotConfiguration: PlotConfiguration,
              private svg: D3Selection<SVGSVGElement>,
  ) {}

  setupAxesOverrides() {
    this.plotConfiguration.sub_plots.forEach((subplot, subplotIndex) => {
      const subplotG = this.svg.select<SVGGElement>(`g.subplot-${subplotIndex}`);
      subplot.axes.forEach((_, axisIndex) => {
        const axisBackground = subplotG.selectChild(`.y-axis-background-${axisIndex}`);
        const axisG = subplotG.selectChild(`.y-axis-${axisIndex}`);
        const axisLabel = subplotG.selectChild(`.y-axis-label-${axisIndex}`);
        const onYAxisClick = this.getOnYAxisClick(subplotIndex, axisIndex);
        axisBackground.on('click', onYAxisClick);
        axisLabel.on('click', onYAxisClick);
        axisG.on('click', onYAxisClick);
      });
    });

    const xAxisBackground = this.svg.selectChild(`.x-axis-background`);
    const xAxisLabel = this.svg.selectChild(`.x-axis-label`);
    const xAxisG = this.svg.select<SVGGElement>('.x-axis');
    const onXAxisClick = this.getOnXAxisClick();
    xAxisBackground.on('click', onXAxisClick);
    xAxisLabel.on('click', onXAxisClick);
    xAxisG.on('click', onXAxisClick);
  }

  private getOnYAxisClick(subplotIndex: number, axisIndex: number) {
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

  private getOnXAxisClick() {
    return (mouseEvent: MouseEvent) => {
      this.store.dispatch(ProcessPlotActions.xAxisClicked({
        data: {
          position: {
            x: mouseEvent.offsetX,
            y: mouseEvent.offsetY,
          },
        },
      }));
    };
  }
}
