import { createFeatureSelector, createSelector } from '@ngrx/store';
import { methodEditorSlice, MethodEditorState } from './method-editor.reducer';

export class MethodEditorSelectors {
  static selectFeature = createFeatureSelector<MethodEditorState>(methodEditorSlice.name);
  static monacoServicesInitialized = createSelector(this.selectFeature, state => state.monacoServicesInitialized);
  static methodEditorIsDirty = createSelector(this.selectFeature, state => state.methodEditorIsDirty);
  static methodEditorContent = createSelector(this.selectFeature, state => state.methodEditorContent);
}
