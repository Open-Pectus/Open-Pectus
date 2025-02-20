import { BaseType, Selection } from 'd3';

// export type D3Selection<T extends BaseType> = Selection<T, unknown, null, any>;
export type D3Selection<T extends BaseType = BaseType, Datum = unknown> = Selection<T, Datum, BaseType, unknown>;

export interface LeftRight {
  left: number;
  right: number;
}

export interface TopBottom {
  top: number;
  bottom: number;
}

export interface Annotation {
  x: number;
  label?: string;
}

export interface ColoredRegionRect {
  start: number;
  end: number;
  color: string;
  value: string | number | undefined;
}

export interface YAxisOverrideDialogData {
  subplotIndex: number;
  axisIndex: number;
  position: {
    x: number;
    y: number;
  };
}

export interface XAxisOverrideDialogData {
  position: {
    x: number;
    y: number;
  };
}

export interface AxisLimits {
  max: number;
  min: number;
}

export type YAxesLimitsOverride = (AxisLimits | null)[][];

export interface ZoomAndPanDomainOverrides {
  x: AxisLimits;
  y: YAxesLimitsOverride;
}
