import { createFeatureSelector } from '@ngrx/store';
import { processValuesSlice, ProcessValuesState } from './process-values.reducer';

export class ProcessValuesSelectors {
  static selectFeature = createFeatureSelector<ProcessValuesState>(processValuesSlice.name);
}
