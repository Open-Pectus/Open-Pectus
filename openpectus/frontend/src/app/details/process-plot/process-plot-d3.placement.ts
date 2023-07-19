import { axisBottom, axisLeft, axisRight, ScaleLinear, Selection, sum } from 'd3';
import { PlotConfiguration, SubPlot } from '../../api';

interface LeftRight {
  left: number;
  right: number;
}

interface TopBottom {
  top: number;
  bottom: number;
}

export class ProcessPlotD3Placement {
  // Configurable values
  private readonly subPlotGap = 20; // also adds to top margin
  private readonly margin = {left: 5, top: 10 - this.subPlotGap, right: 5, bottom: 5};
  private readonly axisGap = 10;
  private readonly axisLabelHeight = 11;

  updateElementPlacements(plotConfiguration: PlotConfiguration, svg: Selection<SVGSVGElement, unknown, null, any> | undefined,
                          xScale: ScaleLinear<number, number>, yScales: ScaleLinear<number, number>[][]) {
    if(svg === undefined) throw Error('no SVG element during placement!');
    const svgHeight = svg.node()?.height.baseVal.value ?? 0;
    const svgWidth = svg.node()?.width.baseVal.value ?? 0;
    const xAxisHeight = svg.select<SVGGElement>('.x-axis').node()?.getBoundingClientRect().height ?? 0;
    const subPlotLeftRight = this.calculatePlotLeftRight(svg, plotConfiguration, svgWidth);

    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = svg.selectChild<SVGGElement>(`.subplot-${subPlotIndex}`);
      const subPlotTopBottom = this.calculateSubPlotTopBottom(plotConfiguration, subPlotIndex, svgHeight, xAxisHeight);
      this.placeYAxes(subPlot, subPlotG, subPlotIndex, yScales, subPlotLeftRight, subPlotTopBottom);
      this.placeSubPlotBorder(subPlotG, subPlotLeftRight, subPlotTopBottom);
    });
    this.placeXAxis(svg, svgHeight, xScale, subPlotLeftRight);
  }

  private placeYAxes(subPlot: SubPlot, subPlotG: Selection<SVGGElement, unknown, null, any>, subPlotIndex: number,
                     yScales: ScaleLinear<number, number>[][], leftRight: LeftRight, topBottom: TopBottom) {
    yScales[subPlotIndex].forEach(yScale => yScale.range([topBottom.top, topBottom.bottom]));
    subPlot.axes.forEach((axis, axisIndex) => {
      const yScale = yScales[subPlotIndex][axisIndex];
      const otherRightSideYAxesWidth = subPlotG.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
                                         .filter((_, otherAxisIndex) => otherAxisIndex !== 0 && otherAxisIndex < axisIndex)
                                         .map(yAxis => yAxis.getBoundingClientRect().width)
                                         .reduce((current, previous) => current + previous + this.axisGap, 0) ?? 0;

      const isLeftAxis = axisIndex === 0;
      const axisXTransform = isLeftAxis ? leftRight.left : leftRight.right + otherRightSideYAxesWidth; // right side

      const axisG = subPlotG.selectChild<SVGGElement>(`.y-axis-${axisIndex}`)
        .call(isLeftAxis ? axisLeft(yScale) : axisRight(yScale))
        .attr('transform', `translate(${[axisXTransform, 0]})`);

      const axisWidth = axisG.node()?.getBoundingClientRect().width ?? 0;
      const axisHeight = topBottom.bottom - topBottom.top;
      const labelWidth = axisG.selectChild<SVGGElement>('text').node()?.getBoundingClientRect().width ?? 0;
      const labelXTransform = isLeftAxis ? -axisWidth : axisWidth;
      const labelYTransform = topBottom.top + axisHeight / 2 - labelWidth / 2;
      const labelRotation = isLeftAxis ? -90 : 90;
      axisG.selectChild('text').text(axis.label)
        .attr('transform', `translate(${[labelXTransform, labelYTransform]})` + `rotate(${labelRotation})`);
    });
  }

  private placeXAxis(svg: Selection<SVGSVGElement, unknown, null, any>, svgHeight: number, xScale: ScaleLinear<number, number>,
                     leftRight: LeftRight) {
    xScale.range([leftRight.left, leftRight.right]);
    svg.selectChild<SVGGElement>('.x-axis')
      .call(axisBottom(xScale))
      .attr('transform', (_, __, selection) => {
        const thisAxisHeight = selection[0].getBoundingClientRect().height;
        return `translate(${[0, svgHeight - this.margin.bottom - thisAxisHeight]})`;
      });
  }

  private placeSubPlotBorder(subPlotG: Selection<SVGGElement, unknown, null, any>,
                             leftRight: LeftRight, topBottom: TopBottom) {
    subPlotG.selectChild<SVGGElement>('.subplot-border')
      .attr('stroke-width', 1)
      .attr('stroke', 'black')
      .attr('fill', 'none')
      .attr('x', leftRight.left)
      .attr('y', topBottom.top)
      // Math.abs() avoids errors with negative values while container is collapsing
      .attr('height', Math.abs(topBottom.bottom - topBottom.top))
      .attr('width', Math.abs(leftRight.right - leftRight.left));
  }

  private calculatePlotLeftRight(svg: Selection<SVGSVGElement, unknown, null, any>, plotConfiguration: PlotConfiguration, svgWidth: number) {
    const widestLeftSideYAxisWidth = this.calculateWidestLeftSideYAxisWidth(svg);
    const widestRightSideYAxisWidth = this.calculateWidestRightSideYAxisWidth(plotConfiguration, svg);
    return {
      left: this.margin.left + widestLeftSideYAxisWidth,
      right: svgWidth - this.margin.right - widestRightSideYAxisWidth,
    };
  }

  private calculateSubPlotTopBottom(plotConfiguration: PlotConfiguration, subPlotIndex: number, svgHeight: number,
                                    xAxisHeight: number): TopBottom {
    const totalRatio = sum(plotConfiguration.sub_plots.map(subPlot => subPlot.ratio));
    const previousSubPlotsRatio = sum(plotConfiguration.sub_plots
      .filter((_, index) => index < subPlotIndex)
      .map(subPlot => subPlot.ratio),
    );
    const followingSubPlotsRatio = sum(plotConfiguration.sub_plots
      .filter((_, index) => index > subPlotIndex)
      .map(subPlot => subPlot.ratio),
    );
    const svgPlotsHeight = svgHeight - this.margin.top - this.margin.bottom - xAxisHeight;
    const subPlotStartOffset = (previousSubPlotsRatio / totalRatio) * svgPlotsHeight;
    const subPlotEndOffset = (followingSubPlotsRatio / totalRatio) * svgPlotsHeight;
    const subPlotTop = this.margin.top + subPlotStartOffset + this.subPlotGap;
    const subPlotBottom = svgHeight - this.margin.bottom - xAxisHeight - subPlotEndOffset;
    return {top: subPlotTop, bottom: subPlotBottom};
  }

  private calculateWidestLeftSideYAxisWidth(svg: Selection<SVGSVGElement, unknown, null, any>) {
    return svg.select<SVGGElement>('.y-axis-0').nodes()
             .map(yAxis => yAxis.getBoundingClientRect().width)
             .reduce((current, previous) => current + previous + this.axisGap + this.axisLabelHeight, 0) - this.axisGap;
  }

  private calculateWidestRightSideYAxisWidth(plotConfiguration: PlotConfiguration, svg: Selection<SVGSVGElement, unknown, null, any>) {
    const rightSideYAxesWidths = plotConfiguration.sub_plots.map((_, subPlotIndex) => {
      const subPlotG = svg.selectChild(`.subplot-${subPlotIndex}`);
      return subPlotG.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
               .filter((_, index) => index > 0)
               .map(yAxis => yAxis.getBoundingClientRect().width)
               .reduce((current, previous) => current + previous + this.axisGap + this.axisLabelHeight, 0) - this.axisGap;
    });
    return Math.max(...rightSideYAxesWidths, 0);
  }
}
