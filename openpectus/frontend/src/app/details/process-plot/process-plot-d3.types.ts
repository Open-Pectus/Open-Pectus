import { BaseType, Selection } from 'd3';

export type D3Selection<T extends BaseType> = Selection<T, unknown, null, any>;

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
