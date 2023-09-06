import { Axis, axisBottom, axisLeft, axisRight, axisTop, NumberValue, ScaleLinear, sum } from 'd3';
import { PlotConfiguration, SubPlot } from '../../api';
import { ProcessPlotD3FontSizes } from './process-plot-d3.font-sizes';
import { D3Selection, LeftRight, TopBottom } from './process-plot-d3.types';

export class ProcessPlotD3Placement {
  xGridLineAxisGenerators: Axis<NumberValue>[] = [];
  // Configurable values
  private readonly subPlotGap = 20;
  private readonly axisGap = 14;
  private readonly yAxisLabelMargin = 8;
  private readonly pixelsPerTick = 42;

  constructor(private svg: D3Selection<SVGSVGElement>,
              private plotConfiguration: PlotConfiguration,
              private xScale: ScaleLinear<number, number>,
              private yScales: ScaleLinear<number, number>[][]) {}

  updateElementPlacements() {
    const svgHeight = this.svg.node()?.height.baseVal.value ?? 0;
    const svgWidth = this.svg.node()?.width.baseVal.value ?? 0;
    const xAxisHeight = this.svg.select<SVGGElement>('.x-axis').node()?.getBoundingClientRect().height ?? 0;
    const subPlotLeftRight = this.calculatePlotLeftRight(this.svg, this.plotConfiguration, svgWidth);
    this.placeXAxis(this.svg, svgHeight, subPlotLeftRight, xAxisHeight);
    const coloredRegionLabelHeight = this.calculateColorRegionLabelsHeight(this.svg, this.plotConfiguration);

    this.plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = this.svg.selectChild<SVGGElement>(`.subplot-${subPlotIndex}`);
      const subPlotTopBottom = this.calculateSubPlotTopBottom(subPlotIndex, svgHeight, xAxisHeight,
        coloredRegionLabelHeight);
      this.placeYAxes(subPlot, subPlotG, subPlotIndex, subPlotLeftRight, subPlotTopBottom);
      this.placeGridLines(subPlotG, subPlotIndex, subPlotLeftRight, subPlotTopBottom);
      this.placeSubPlotBorder(subPlotG, subPlotLeftRight, subPlotTopBottom);
    });

    this.updateAxes();
  }

  updateAxes() {
    this.svg.selectChild<SVGGElement>('.x-axis').call(axisBottom(this.xScale));
    this.plotConfiguration.sub_plots.forEach((subPlot, subPlotIndex) => {
      const subPlotG = this.svg.selectChild<SVGGElement>(`.subplot-${subPlotIndex}`);
      subPlot.axes.forEach((_, axisIndex) => {
        const yScale = this.yScales[subPlotIndex][axisIndex];
        const isLeftAxis = axisIndex === 0;
        const axisGenerator = isLeftAxis ? axisLeft(yScale) : axisRight(yScale);
        axisGenerator.tickFormat((tickValue: NumberValue) => tickValue.valueOf().toFixed(1));
        axisGenerator.tickValues(this.getTickValues(yScale));
        subPlotG.selectChild<SVGGElement>(`.y-axis-${axisIndex}`).call(axisGenerator);
      });
    });
  }

  private placeYAxes(subPlot: SubPlot,
                     subPlotG: D3Selection<SVGGElement>,
                     subPlotIndex: number,
                     leftRight: LeftRight,
                     topBottom: TopBottom) {
    this.yScales[subPlotIndex].forEach(yScale => yScale.range([topBottom.bottom, topBottom.top]));
    subPlot.axes.forEach((_, axisIndex) => {
      const axisXTransform = this.placeYAxis(axisIndex, subPlotG, leftRight);
      this.placeAxisLabelAndBackground(axisIndex, subPlotG, topBottom, axisXTransform);
    });
  }

  private placeYAxis(axisIndex: number,
                     subPlotG: D3Selection<SVGGElement>,
                     leftRight: LeftRight) {
    const otherRightSideYAxesWidth = subPlotG.selectChildren<SVGGElement, unknown>('.y-axis').nodes()
                                       .filter((_, otherAxisIndex) => otherAxisIndex !== 0 && otherAxisIndex < axisIndex)
                                       .map(this.mapYAxisWidth.bind(this))
                                       .reduce((current, previous) => current + previous, 0) ?? 0;
    const isLeftAxis = axisIndex === 0;
    const yAxisXTransform = isLeftAxis ? leftRight.left : leftRight.right + otherRightSideYAxesWidth; // right side
    subPlotG.selectChild<SVGGElement>(`.y-axis-${axisIndex}`)
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
    return yAxis.getBoundingClientRect().width + this.axisGap + ProcessPlotD3FontSizes.axisLabelSize + this.yAxisLabelMargin;
  }

  private placeAxisLabelAndBackground(axisIndex: number, subPlotG: D3Selection<SVGGElement>, topBottom: TopBottom,
                                      axisXTransform: number) {
    const isLeftAxis = axisIndex === 0;
    const axisWidth = subPlotG.selectChild<SVGGElement>(`.y-axis-${axisIndex}`).node()?.getBoundingClientRect().width ?? 0;
    const axisHeight = topBottom.bottom - topBottom.top;
    const labelWidth = subPlotG.selectChild<SVGGElement>(`.axis-label-${axisIndex}`).node()?.getBoundingClientRect().height ?? 0;
    const labelRotation = isLeftAxis ? -90 : 90;
    const labelXTransform = axisXTransform + (isLeftAxis ? -axisWidth - this.yAxisLabelMargin : axisWidth + this.yAxisLabelMargin);
    const labelYTransform = topBottom.top + (axisHeight / 2) + (isLeftAxis ? (labelWidth / 2) : -(labelWidth / 2));
    const labelSize = ProcessPlotD3FontSizes.axisLabelSize;
    subPlotG.selectChild(`.axis-label-${axisIndex}`)
      .attr('transform', `translate(${[labelXTransform, labelYTransform]}) rotate(${labelRotation})`)
      .style('font-size', labelSize);

    subPlotG.selectChild(`.y-axis-background-${axisIndex}`)
      .attr('x', isLeftAxis ? labelXTransform - labelSize : axisXTransform)
      .attr('y', topBottom.top)
      .attr('width', axisWidth + this.yAxisLabelMargin + labelSize)
      .attr('height', axisHeight);
  }

  private placeXAxis(svg: D3Selection<SVGSVGElement>, svgHeight: number,
                     leftRight: LeftRight, xAxisHeight: number) {
    this.xScale.range([leftRight.left, leftRight.right]);
    svg.selectChild<SVGGElement>('.x-axis')
      .attr('transform', `translate(${[0, svgHeight - xAxisHeight]})`);
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

  private calculatePlotLeftRight(svg: D3Selection<SVGSVGElement>, plotConfiguration: PlotConfiguration, svgWidth: number) {
    const widestLeftSideYAxisWidth = this.calculateWidestLeftSideYAxisWidth(svg);
    const widestRightSideYAxesWidth = this.calculateWidestRightSideYAxesWidth(plotConfiguration, svg);
    return {
      left: widestLeftSideYAxisWidth,
      right: svgWidth - widestRightSideYAxesWidth,
    };
  }

  private calculateSubPlotTopBottom(subPlotIndex: number, svgHeight: number,
                                    xAxisHeight: number, coloredRegionLabelHeight: number): TopBottom {
    const totalRatio = sum(this.plotConfiguration.sub_plots.map(subPlot => subPlot.ratio));
    const previousSubPlotsRatio = sum(this.plotConfiguration.sub_plots
      .filter((_, index) => index < subPlotIndex)
      .map(subPlot => subPlot.ratio),
    );
    const followingSubPlotsRatio = sum(this.plotConfiguration.sub_plots
      .filter((_, index) => index > subPlotIndex)
      .map(subPlot => subPlot.ratio),
    );
    const firstSubPlotOffset = coloredRegionLabelHeight - this.subPlotGap;
    const allPlotsHeight = svgHeight - xAxisHeight - firstSubPlotOffset;
    const subPlotStartOffset = (previousSubPlotsRatio / totalRatio) * allPlotsHeight;
    const subPlotEndOffset = (followingSubPlotsRatio / totalRatio) * allPlotsHeight;
    const subPlotTop = firstSubPlotOffset + subPlotStartOffset + this.subPlotGap;
    const subPlotBottom = svgHeight - xAxisHeight - subPlotEndOffset;
    return {top: subPlotTop, bottom: subPlotBottom};
  }

  private calculateColorRegionLabelsHeight(svg: D3Selection<SVGSVGElement>, plotConfiguration: PlotConfiguration) {
    // measure height of colored region labels
    const colorRegionHeights = plotConfiguration.color_regions.map((_, colorRegionIndex) => {
      const colorRegionG = svg.select<SVGGElement>(`.color-region-${colorRegionIndex}`);
      const rect = colorRegionG.select<SVGRectElement>('rect');
      const totalHeight = colorRegionG.node()?.getBoundingClientRect()?.height ?? 0;
      const rectBoundingRectangle = rect.node()?.getBoundingClientRect();
      // if the rect width is 0 it will not actually contribute to the totalHeight, but will return full height from boundingRectangle. So disregard the value when width is 0
      const rectHeight = rectBoundingRectangle?.width === 0 ? 0 : rectBoundingRectangle?.height ?? 0;
      return totalHeight - rectHeight;
    });

    // measure height of annotation labels
    const annotationsSelection = svg.select<SVGGElement>('.annotations');
    const annotationLineSelection = annotationsSelection.select<SVGLineElement>('line');
    const totalHeight = annotationsSelection.node()?.getBoundingClientRect()?.height ?? 0;
    const lineHeight = annotationLineSelection.node()?.getBoundingClientRect()?.height ?? 0;
    const annotationsHeight = totalHeight - lineHeight;

    // return max height, ensuring -Infinity is not possible.
    return Math.max(...colorRegionHeights, annotationsHeight, 0);
  }

  private calculateWidestLeftSideYAxisWidth(svg: D3Selection<SVGSVGElement>) {
    return svg.select<SVGGElement>('.y-axis-0').nodes()
             .map(this.mapYAxisWidth.bind(this))
             .reduce((current, previous) => previous + current, 0) - this.axisGap;
  }

  private calculateWidestRightSideYAxesWidth(plotConfiguration: PlotConfiguration, svg: D3Selection<SVGSVGElement>) {
    const rightSideYAxesWidths = plotConfiguration.sub_plots.map((_, subPlotIndex) => {
      const subPlotG = svg.selectChild<SVGGElement>(`.subplot-${subPlotIndex}`);
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
