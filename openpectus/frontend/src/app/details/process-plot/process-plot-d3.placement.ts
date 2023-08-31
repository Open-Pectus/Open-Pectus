import { Axis, axisBottom, axisLeft, axisRight, axisTop, NumberValue, ScaleLinear, sum } from 'd3';
import { PlotConfiguration, SubPlot } from '../../api';
import { D3Selection, LeftRight, TopBottom } from './process-plot-d3.types';

export class ProcessPlotD3Placement {
  xGridLineAxisGenerators: Axis<NumberValue>[] = [];
  private readonly axisLabelHeight = 12;
  // Configurable values
  private readonly subPlotGap = 20;
  private readonly margin = {left: 5, top: 10, right: 5, bottom: 5};
  private readonly axisGap = 14;
  private readonly yAxisLabelMargin = 8;
  private readonly pixelsPerTick = 42;

  constructor(private plotConfiguration: PlotConfiguration,
              private svg: D3Selection<SVGSVGElement>,
              private xScale: ScaleLinear<number, number>,
              private yScales: ScaleLinear<number, number>[][]) {}

  updateElementPlacements() {
    const rootHeight = (this.svg.node()?.height.baseVal.value ?? 0) - this.margin.top - this.margin.bottom;
    const rootWidth = (this.svg.node()?.width.baseVal.value ?? 0) - this.margin.left - this.margin.right;
    const root = this.svg.selectChild<SVGGElement>('.root').attr('transform', `translate(${[this.margin.left, this.margin.top]})`);
    const xAxisHeight = root.select<SVGGElement>('.x-axis').node()?.getBoundingClientRect().height ?? 0;
    const subPlotLeftRight = this.calculatePlotLeftRight(root, this.plotConfiguration, rootWidth);
    this.placeXAxis(root, rootHeight, subPlotLeftRight, xAxisHeight);
    const coloredRegionLabelHeight = this.calculateColorRegionLabelsHeight(root, this.plotConfiguration);

    this.plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = root.selectChild<SVGGElement>(`.subplot-${subPlotIndex}`);
      const subPlotTopBottom = this.calculateSubPlotTopBottom(this.plotConfiguration, subPlotIndex, rootHeight, xAxisHeight,
        coloredRegionLabelHeight);
      this.placeYAxes(subPlot, subPlotG, subPlotIndex, subPlotLeftRight, subPlotTopBottom);
      this.placeGridLines(subPlotG, subPlotIndex, subPlotLeftRight, subPlotTopBottom);
      this.placeSubPlotBorder(subPlotG, subPlotLeftRight, subPlotTopBottom);
    });
  }

  private placeYAxes(subPlot: SubPlot, subPlotG: D3Selection<SVGGElement>,
                     subPlotIndex: number,
                     leftRight: LeftRight,
                     topBottom: TopBottom) {
    this.yScales[subPlotIndex].forEach(yScale => yScale.range([topBottom.bottom, topBottom.top]));
    subPlot.axes.forEach((_, axisIndex) => {
      const axisXTransform = this.placeYAxis(subPlotIndex, axisIndex, subPlotG, leftRight);
      this.placeAxisLabels(axisIndex, subPlotG, topBottom, axisXTransform);
    });
  }

  private placeYAxis(subPlotIndex: number, axisIndex: number,
                     subPlotG: D3Selection<SVGGElement>, leftRight: LeftRight) {
    const yScale = this.yScales[subPlotIndex][axisIndex];
    const otherRightSideYAxesWidth = subPlotG.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
                                       .filter((_, otherAxisIndex) => otherAxisIndex !== 0 && otherAxisIndex < axisIndex)
                                       .map(this.mapYAxisWidth.bind(this))
                                       .reduce((current, previous) => current + previous, 0) ?? 0;
    const isLeftAxis = axisIndex === 0;
    const yAxisXTransform = isLeftAxis ? leftRight.left : leftRight.right + otherRightSideYAxesWidth; // right side
    const axisGenerator = isLeftAxis ? axisLeft(yScale) : axisRight(yScale);
    axisGenerator.tickValues(this.getTickValues(yScale));
    subPlotG.selectChild<SVGGElement>(`.y-axis-${axisIndex}`)
      .call(axisGenerator)
      .attr('transform', `translate(${[yAxisXTransform, 0]})`);
    return yAxisXTransform;
  }

  private getTickValues(yScale: ScaleLinear<number, number>) {
    const [domainMin, domainMax] = yScale.domain();
    const [rangeMaxY, rangeMinY] = yScale.range(); // max before min because svg y 0 is at the top, so the range goes from high y to low y.
    const ticksAmount = Math.floor((rangeMaxY - rangeMinY) / this.pixelsPerTick);
    if(ticksAmount < 0) return []; // while expanding, this can be temporarily negative throwing errors in console. So let's avoid that.
    const domainSlice = (domainMax - domainMin) / (ticksAmount - 1);
    return new Array(ticksAmount).fill(undefined).map((_, index) => domainMin + index * domainSlice);
  }

  private mapYAxisWidth(yAxis: SVGGElement) {
    return yAxis.getBoundingClientRect().width + this.axisGap + this.axisLabelHeight + this.yAxisLabelMargin;
  }

  private placeAxisLabels(axisIndex: number, subPlotG: D3Selection<SVGGElement>, topBottom: TopBottom,
                          axisXTransform: number) {
    const isLeftAxis = axisIndex === 0;
    const axisWidth = subPlotG.selectChild<SVGGElement>(`.y-axis-${axisIndex}`).node()?.getBoundingClientRect().width ?? 0;
    const axisHeight = topBottom.bottom - topBottom.top;
    const labelWidth = subPlotG.selectChild<SVGGElement>(`.axis-label-${axisIndex}`).node()?.getBoundingClientRect().height ?? 0;
    const labelRotation = isLeftAxis ? -90 : 90;
    const labelXTransform = axisXTransform + (isLeftAxis ? -axisWidth - this.yAxisLabelMargin : axisWidth + this.yAxisLabelMargin);
    const labelYTransform = topBottom.top + (axisHeight / 2) + (isLeftAxis ? (labelWidth / 2) : -(labelWidth / 2));
    subPlotG.selectChild(`.axis-label-${axisIndex}`)
      .attr('transform', `translate(${[labelXTransform, labelYTransform]}) rotate(${labelRotation})`)
      .style('font-size', this.axisLabelHeight);
  }

  private placeXAxis(root: D3Selection<SVGGElement>, rootHeight: number,
                     leftRight: LeftRight, xAxisHeight: number) {
    this.xScale.range([leftRight.left, leftRight.right]);
    root.selectChild<SVGGElement>('.x-axis')
      .call(axisBottom(this.xScale))
      .attr('transform', `translate(${[0, rootHeight - xAxisHeight]})`);
  }

  private placeSubPlotBorder(subPlotG: D3Selection<SVGGElement>,
                             leftRight: LeftRight, topBottom: TopBottom) {
    const borderSelection = subPlotG.selectChild<SVGGElement>('.subplot-border');
    [borderSelection.selectChild<SVGRectElement>('rect'),
      borderSelection.selectChild<SVGClipPathElement>('clipPath').selectChild<SVGRectElement>('rect'),
    ].forEach(rect => {
      rect
        .attr('x', leftRight.left)
        .attr('y', topBottom.top)
        // Math.abs() avoids errors with negative values while container is collapsing
        .attr('height', Math.abs(topBottom.bottom - topBottom.top))
        .attr('width', Math.abs(leftRight.right - leftRight.left));
    });
  }

  private calculatePlotLeftRight(root: D3Selection<SVGGElement>, plotConfiguration: PlotConfiguration, rootWidth: number) {
    const widestLeftSideYAxisWidth = this.calculateWidestLeftSideYAxisWidth(root);
    const widestRightSideYAxesWidth = this.calculateWidestRightSideYAxesWidth(plotConfiguration, root);
    return {
      left: widestLeftSideYAxisWidth,
      right: rootWidth - widestRightSideYAxesWidth,
    };
  }

  private calculateSubPlotTopBottom(plotConfiguration: PlotConfiguration, subPlotIndex: number, rootHeight: number,
                                    xAxisHeight: number, coloredRegionLabelHeight: number): TopBottom {
    const totalRatio = sum(plotConfiguration.sub_plots.map(subPlot => subPlot.ratio));
    const previousSubPlotsRatio = sum(plotConfiguration.sub_plots
      .filter((_, index) => index < subPlotIndex)
      .map(subPlot => subPlot.ratio),
    );
    const followingSubPlotsRatio = sum(plotConfiguration.sub_plots
      .filter((_, index) => index > subPlotIndex)
      .map(subPlot => subPlot.ratio),
    );
    const firstSubPlotOffset = coloredRegionLabelHeight - this.subPlotGap;
    const allPlotsHeight = rootHeight - xAxisHeight - firstSubPlotOffset;
    const subPlotStartOffset = (previousSubPlotsRatio / totalRatio) * allPlotsHeight;
    const subPlotEndOffset = (followingSubPlotsRatio / totalRatio) * allPlotsHeight;
    const subPlotTop = firstSubPlotOffset + subPlotStartOffset + this.subPlotGap;
    const subPlotBottom = rootHeight - xAxisHeight - subPlotEndOffset;
    return {top: subPlotTop, bottom: subPlotBottom};
  }

  private calculateColorRegionLabelsHeight(root: D3Selection<SVGGElement>, plotConfiguration: PlotConfiguration) {
    // measure height of colored region labels
    const colorRegionHeights = plotConfiguration.color_regions.map((_, colorRegionIndex) => {
      const colorRegionG = root.select<SVGGElement>(`.color-region-${colorRegionIndex}`);
      const rect = colorRegionG.select<SVGRectElement>('rect');
      const totalHeight = colorRegionG.node()?.getBoundingClientRect()?.height ?? 0;
      const rectBoundingRectangle = rect.node()?.getBoundingClientRect();
      // if the rect width is 0 it will not actually contribute to the totalHeight, but will return full height from boundingRectangle. So disregard the value when width is 0
      const rectHeight = rectBoundingRectangle?.width === 0 ? 0 : rectBoundingRectangle?.height ?? 0;
      return totalHeight - rectHeight;
    });

    // measure height of annotation labels
    const annotationsSelection = root.select<SVGGElement>('.annotations');
    const annotationLineSelection = annotationsSelection.select<SVGLineElement>('line');
    const totalHeight = annotationsSelection.node()?.getBoundingClientRect()?.height ?? 0;
    const lineHeight = annotationLineSelection.node()?.getBoundingClientRect()?.height ?? 0;
    const annotationsHeight = totalHeight - lineHeight;

    // return max height, ensuring -Infinity is not possible.
    return Math.max(...colorRegionHeights, annotationsHeight, 0);
  }

  private calculateWidestLeftSideYAxisWidth(root: D3Selection<SVGGElement>) {
    return root.select<SVGGElement>('.y-axis-0').nodes()
             .map(this.mapYAxisWidth.bind(this))
             .reduce((current, previous) => previous + current, 0) - this.axisGap;
  }

  private calculateWidestRightSideYAxesWidth(plotConfiguration: PlotConfiguration, root: D3Selection<SVGGElement>) {
    const rightSideYAxesWidths = plotConfiguration.sub_plots.map((_, subPlotIndex) => {
      const subPlotG = root.selectChild<SVGGElement>(`.subplot-${subPlotIndex}`);
      return subPlotG.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
               .filter((_, index) => index > 0)
               .map(this.mapYAxisWidth.bind(this))
               .reduce((current, previous) => previous + current, 0) - this.axisGap;
    });
    return Math.max(...rightSideYAxesWidths, 0);
  }

  private placeGridLines(subPlotG: D3Selection<SVGGElement>, subPlotIndex: number,
                         subPlotLeftRight: { left: number; right: number },
                         subPlotTopBottom: TopBottom) {
    const subPlotWidth = subPlotLeftRight.right - subPlotLeftRight.left;
    const subPlotHeight = subPlotTopBottom.bottom - subPlotTopBottom.top;
    this.xGridLineAxisGenerators[subPlotIndex] = axisTop(this.xScale)
      .tickSize(-subPlotHeight)
      .tickFormat(() => '');
    subPlotG.select<SVGGElement>('.x-grid-lines')
      .call(this.xGridLineAxisGenerators[subPlotIndex])
      .attr('transform', `translate(${[0, subPlotTopBottom.top]})`);

    const yScale = this.yScales[subPlotIndex][0];
    subPlotG.select<SVGGElement>('.y-grid-lines')
      .call(axisLeft(yScale)
        .tickSize(-subPlotWidth)
        .tickFormat(() => '')
        .tickValues(this.getTickValues(yScale)))
      .attr('transform', `translate(${[subPlotLeftRight.left, 0]})`);

  }
}
