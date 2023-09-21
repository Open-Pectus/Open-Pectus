import { createFeatureSelector, createSelector } from '@ngrx/store';
import { methodEditorSlice, MethodEditorState } from './method-editor.reducer';

export class MethodEditorSelectors {
  static selectFeature = createFeatureSelector<MethodEditorState>(methodEditorSlice.name);
  static monacoServicesInitialized = createSelector(this.selectFeature, state => state.monacoServicesInitialized);
  static isDirty = createSelector(this.selectFeature, state => state.isDirty);
  static content = createSelector(this.selectFeature, state => state.content);
  static lockedLines = createSelector(this.selectFeature, state => state.lockedLines);
  static injectedLines = createSelector(this.selectFeature, state => state.injectedLines);
}
