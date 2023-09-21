import { createFeatureSelector, createSelector } from '@ngrx/store';
import { methodEditorSlice, MethodEditorState } from './method-editor.reducer';

export class MethodEditorSelectors {
  static selectFeature = createFeatureSelector<MethodEditorState>(methodEditorSlice.name);
  static monacoServicesInitialized = createSelector(this.selectFeature, state => state.monacoServicesInitialized);
  static isDirty = createSelector(this.selectFeature, state => state.isDirty);
  static method = createSelector(this.selectFeature, state => state.method);
  static methodContent = createSelector(this.method, method => method.lines.map(line => line.content).join('\n'));
  static lineIds = createSelector(this.method, method => method.lines.map(line => line.id));
  static injectedLineIds = createSelector(this.method, method => method.lines.filter(line => line.is_injected).map(line => line.id));
  static lockedLineIds = createSelector(this.method, method => method.lines.filter(line => line.is_locked).map(line => line.id));
}
