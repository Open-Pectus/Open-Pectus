import { Axis, axisBottom, axisLeft, axisRight, axisTop, NumberValue, ScaleLinear, Selection, sum } from 'd3';
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
  xGridLineAxisGenerators: Axis<NumberValue>[] = [];
  // Configurable values
  private readonly subPlotGap = 20; // also adds to top margin
  private readonly margin = {left: 5, top: 10 - this.subPlotGap, right: 5, bottom: 5};
  private readonly axisGap = 14;
  private readonly labelMargin = 8;
  private readonly pixelsPerTick = 42;

  updateElementPlacements(plotConfiguration: PlotConfiguration, svg: Selection<SVGSVGElement, unknown, null, any> | undefined,
                          xScale: ScaleLinear<number, number>, yScales: ScaleLinear<number, number>[][]) {
    if(svg === undefined) throw Error('no SVG element during placement!');
    const rootHeight = (svg.node()?.height.baseVal.value ?? 0) - this.margin.top - this.margin.bottom;
    const rootWidth = (svg.node()?.width.baseVal.value ?? 0) - this.margin.left - this.margin.right;
    const root = svg.selectChild<SVGGElement>('.root').attr('transform', `translate(${[this.margin.left, this.margin.top]})`);
    const xAxisHeight = root.select<SVGGElement>('.x-axis').node()?.getBoundingClientRect().height ?? 0;
    const subPlotLeftRight = this.calculatePlotLeftRight(root, plotConfiguration, rootWidth);

    this.placeXAxis(root, rootHeight, xScale, subPlotLeftRight, xAxisHeight);
    plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = root.selectChild<SVGGElement>(`.subplot-${subPlotIndex}`);
      const subPlotTopBottom = this.calculateSubPlotTopBottom(plotConfiguration, subPlotIndex, rootHeight, xAxisHeight);
      this.placeYAxes(subPlot, subPlotG, subPlotIndex, yScales, subPlotLeftRight, subPlotTopBottom);
      this.placeGridLines(subPlot, subPlotG, subPlotIndex, xScale, yScales, subPlotLeftRight, subPlotTopBottom);
      this.placeSubPlotBorder(subPlotG, subPlotLeftRight, subPlotTopBottom);
    });
  }

  private placeYAxes(subPlot: SubPlot, subPlotG: Selection<SVGGElement, unknown, null, any>, subPlotIndex: number,
                     yScales: ScaleLinear<number, number>[][], leftRight: LeftRight, topBottom: TopBottom) {
    yScales[subPlotIndex].forEach(yScale => yScale.range([topBottom.top, topBottom.bottom]));
    subPlot.axes.forEach((axis, axisIndex) => {
      const axisXTransform = this.placeYAxis(yScales, subPlotIndex, axisIndex, subPlotG, leftRight);
      this.placeAxisLabels(axisIndex, subPlotG, topBottom, axisXTransform);
    });
  }

  private placeYAxis(yScales: ScaleLinear<number, number>[][], subPlotIndex: number, axisIndex: number,
                     subPlotG: Selection<SVGGElement, unknown, null, any>, leftRight: LeftRight) {
    const yScale = yScales[subPlotIndex][axisIndex];
    const otherRightSideYAxesWidth = subPlotG.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
                                       .filter((_, otherAxisIndex) => otherAxisIndex !== 0 && otherAxisIndex < axisIndex)
                                       .map(this.mapYAxisWidth.bind(this))
                                       .reduce((current, previous) => current + previous, 0) ?? 0;
    const tickValues = this.getTickValues(yScale);
    const isLeftAxis = axisIndex === 0;
    const axisXTransform = isLeftAxis ? leftRight.left : leftRight.right + otherRightSideYAxesWidth; // right side
    subPlotG.selectChild<SVGGElement>(`.y-axis-${axisIndex}`)
      .call(isLeftAxis ? axisLeft(yScale).tickValues(tickValues) : axisRight(yScale).tickValues(tickValues))
      .attr('transform', `translate(${[axisXTransform, 0]})`);
    // noinspection JSSuspiciousNameCombination
    return axisXTransform;
  }

  private getTickValues(yScale: ScaleLinear<number, number>) {
    const [domainMin, domainMax] = yScale.domain();
    const [rangeMin, rangeMax] = yScale.range();
    const ticksAmount = Math.floor((rangeMax - rangeMin) / this.pixelsPerTick);
    const domainSlice = (domainMax - domainMin) / (ticksAmount - 1);
    return new Array(ticksAmount).fill(undefined).map((_, index) => domainMin + index * domainSlice);
  }

  private mapYAxisWidth(yAxis: SVGGElement) {
    return yAxis.getBoundingClientRect().width + this.axisGap + this.axisLabelHeight + this.labelMargin;
  }

  private placeAxisLabels(axisIndex: number, subPlotG: Selection<SVGGElement, unknown, null, any>, topBottom: TopBottom,
                          axisXTransform: number) {
    const isLeftAxis = axisIndex === 0;
    const axisWidth = subPlotG.selectChild<SVGGElement>(`.y-axis-${axisIndex}`).node()?.getBoundingClientRect().width ?? 0;
    const axisHeight = topBottom.bottom - topBottom.top;
    const labelWidth = subPlotG.selectChild<SVGGElement>(`.axis-label-${axisIndex}`).node()?.getBoundingClientRect().height ?? 0;
    const labelRotation = isLeftAxis ? -90 : 90;
    const labelXTransform = axisXTransform + (isLeftAxis ? -axisWidth - this.labelMargin : axisWidth + this.labelMargin);
    const labelYTransform = topBottom.top + (axisHeight / 2) + (isLeftAxis ? (labelWidth / 2) : -(labelWidth / 2));
    subPlotG.selectChild(`.axis-label-${axisIndex}`)
      .attr('transform', `translate(${[labelXTransform, labelYTransform]}) rotate(${labelRotation})`);
  }

  private placeXAxis(root: Selection<SVGGElement, unknown, null, any>, rootHeight: number, xScale: ScaleLinear<number, number>,
                     leftRight: LeftRight, xAxisHeight: number) {
    xScale.range([leftRight.left, leftRight.right]);
    root.selectChild<SVGGElement>('.x-axis')
      .call(axisBottom(xScale))
      .attr('transform', `translate(${[0, rootHeight - xAxisHeight]})`);
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

  private calculatePlotLeftRight(root: Selection<SVGGElement, unknown, null, any>, plotConfiguration: PlotConfiguration, rootWidth: number) {
    const widestLeftSideYAxisWidth = this.calculateWidestLeftSideYAxisWidth(root);
    const widestRightSideYAxesWidth = this.calculateWidestRightSideYAxesWidth(plotConfiguration, root);
    return {
      left: widestLeftSideYAxisWidth,
      right: rootWidth - widestRightSideYAxesWidth,
    };
  }

  private calculateSubPlotTopBottom(plotConfiguration: PlotConfiguration, subPlotIndex: number, rootHeight: number,
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
    const allPlotsHeight = rootHeight - xAxisHeight;
    const subPlotStartOffset = (previousSubPlotsRatio / totalRatio) * allPlotsHeight;
    const subPlotEndOffset = (followingSubPlotsRatio / totalRatio) * allPlotsHeight;
    const subPlotTop = subPlotStartOffset + this.subPlotGap;
    const subPlotBottom = rootHeight - xAxisHeight - subPlotEndOffset;
    return {top: subPlotTop, bottom: subPlotBottom};
  }

  private calculateWidestLeftSideYAxisWidth(root: Selection<SVGGElement, unknown, null, any>) {
    return root.select<SVGGElement>('.y-axis-0').nodes()
             .map(this.mapYAxisWidth.bind(this))
             .reduce((current, previous) => previous + current, 0) - this.axisGap;
  }

  private calculateWidestRightSideYAxesWidth(plotConfiguration: PlotConfiguration, root: Selection<SVGGElement, unknown, null, any>) {
    const rightSideYAxesWidths = plotConfiguration.sub_plots.map((_, subPlotIndex) => {
      const subPlotG = root.selectChild<SVGGElement>(`.subplot-${subPlotIndex}`);
      return subPlotG.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
               .filter((_, index) => index > 0)
               .map(this.mapYAxisWidth.bind(this))
               .reduce((current, previous) => previous + current, 0) - this.axisGap;
    });
    return Math.max(...rightSideYAxesWidths, 0);
  }

  private placeGridLines(subPlot: SubPlot, subPlotG: Selection<SVGGElement, unknown, null, any>, subPlotIndex: number,
                         xScale: ScaleLinear<number, number>, yScales: ScaleLinear<number, number>[][],
                         subPlotLeftRight: { left: number; right: number }, subPlotTopBottom: TopBottom) {
    const subPlotWidth = subPlotLeftRight.right - subPlotLeftRight.left;
    const subPlotHeight = subPlotTopBottom.bottom - subPlotTopBottom.top;
    this.xGridLineAxisGenerators[subPlotIndex] = axisTop(xScale)
      .tickSize(-subPlotHeight)
      .tickFormat(() => '');
    subPlotG.select<SVGGElement>('.x-grid-lines')
      .call(this.xGridLineAxisGenerators[subPlotIndex])
      .attr('transform', `translate(${[0, subPlotTopBottom.top]})`);

    const yScale = yScales[subPlotIndex][0];
    subPlotG.select<SVGGElement>('.y-grid-lines')
      .call(axisLeft(yScale)
        .tickSize(-subPlotWidth)
        .tickFormat(() => '')
        .tickValues(this.getTickValues(yScale)))
      .attr('transform', `translate(${[subPlotLeftRight.left, 0]})`);

  }
}
