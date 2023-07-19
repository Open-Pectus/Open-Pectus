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
  readonly axisLabelHeight = 12;
  // Configurable values
  private readonly subPlotGap = 20; // also adds to top margin
  private readonly margin = {left: 5, top: 10 - this.subPlotGap, right: 5, bottom: 5};
  private readonly axisGap = 14;
  private readonly labelMargin = 8;

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
      const axisXTransform = this.placeYAxis(yScales, subPlotIndex, axisIndex, subPlotG, leftRight);
      this.placeAxisLabel(axisIndex, subPlotG, topBottom, axisXTransform);
    });
  }

  private placeYAxis(yScales: ScaleLinear<number, number>[][], subPlotIndex: number, axisIndex: number,
                     subPlotG: Selection<SVGGElement, unknown, null, any>, leftRight: LeftRight) {
    const yScale = yScales[subPlotIndex][axisIndex];
    const otherRightSideYAxesWidth = subPlotG.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
                                       .filter((_, otherAxisIndex) => otherAxisIndex !== 0 && otherAxisIndex < axisIndex)
                                       .map(this.mapYAxisWidth.bind(this))
                                       .reduce((current, previous) => current + previous, 0) ?? 0;

    const isLeftAxis = axisIndex === 0;
    const axisXTransform = isLeftAxis ? leftRight.left : leftRight.right + otherRightSideYAxesWidth; // right side
    subPlotG.selectChild<SVGGElement>(`.y-axis-${axisIndex}`)
      .call(isLeftAxis ? axisLeft(yScale) : axisRight(yScale))
      .attr('transform', `translate(${[axisXTransform, 0]})`);
    // noinspection JSSuspiciousNameCombination
    return axisXTransform;
  }

  private mapYAxisWidth(yAxis: SVGGElement) {
    return yAxis.getBoundingClientRect().width + this.axisGap + this.axisLabelHeight + this.labelMargin;
  }

  private placeAxisLabel(axisIndex: number, subPlotG: Selection<SVGGElement, unknown, null, any>, topBottom: TopBottom,
                         axisXTransform: number) {
    const isLeftAxis = axisIndex === 0;
    const axisWidth = subPlotG.selectChild<SVGGElement>(`.y-axis-${axisIndex}`).node()?.getBoundingClientRect().width ?? 0;
    const axisHeight = topBottom.bottom - topBottom.top;
    const labelWidth = subPlotG.selectChild<SVGGElement>(`.axis-label-${axisIndex}`).node()?.getBoundingClientRect().height ?? 0;
    console.log({labelWidth});
    const labelRotation = isLeftAxis ? -90 : 90;
    const labelXTransform = axisXTransform + (isLeftAxis ? -axisWidth - this.labelMargin : axisWidth + this.labelMargin);
    const labelYTransform = topBottom.top + (axisHeight / 2) + (isLeftAxis ? (labelWidth / 2) : -(labelWidth / 2));
    subPlotG.selectChild(`.axis-label-${axisIndex}`)
      .attr('transform', `translate(${[labelXTransform, labelYTransform]}) rotate(${labelRotation})`);
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
    const widestRightSideYAxesWidth = this.calculateWidestRightSideYAxesWidth(plotConfiguration, svg);
    return {
      left: this.margin.left + widestLeftSideYAxisWidth,
      right: svgWidth - this.margin.right - widestRightSideYAxesWidth,
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
             .map(this.mapYAxisWidth.bind(this))
             .reduce((current, previous) => previous + current, 0) - this.axisGap;
  }

  private calculateWidestRightSideYAxesWidth(plotConfiguration: PlotConfiguration, svg: Selection<SVGSVGElement, unknown, null, any>) {
    const rightSideYAxesWidths = plotConfiguration.sub_plots.map((_, subPlotIndex) => {
      const subPlotG = svg.selectChild<SVGGElement>(`.subplot-${subPlotIndex}`);
      return subPlotG.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
               .filter((_, index) => index > 0)
               .map(this.mapYAxisWidth.bind(this))
               .reduce((current, previous) => previous + current, 0) - this.axisGap;
    });
    return Math.max(...rightSideYAxesWidths, 0);
  }
}
