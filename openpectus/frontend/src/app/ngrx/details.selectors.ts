import { createFeatureSelector, createSelector } from '@ngrx/store';
import { detailsFeatureKey, DetailsState } from './details.reducer';

export class DetailsSelectors {
  static selectFeature = createFeatureSelector<DetailsState>(detailsFeatureKey);
  static methodEditorIsDirty = createSelector(this.selectFeature, state => state.methodEditorIsDirty);
  static methodEditorContent = createSelector(this.selectFeature, state => state.methodEditorContent);
}
