import { createFeatureSelector, createSelector } from '@ngrx/store';
import { methodEditorSlice, MethodEditorState } from './method-editor.reducer';

export class MethodEditorSelectors {
  static selectFeature = createFeatureSelector<MethodEditorState>(methodEditorSlice.name);
  static monacoServicesInitialized = createSelector(this.selectFeature, state => state.monacoServicesInitialized);
  static isDirty = createSelector(this.selectFeature, state => state.isDirty);
  static method = createSelector(this.selectFeature, state => state.method);
  static methodLines = createSelector(this.method, method => method.lines);
  static methodContent = createSelector(this.methodLines, methodLines => methodLines.map(line => line.content).join('\n'));
  static lineIds = createSelector(this.methodLines, methodLines => methodLines.map(line => line.id));
  static injectedLineIds = createSelector(this.method, method => method.injected_line_ids);
  static executedLineIds = createSelector(this.method, method => method.executed_line_ids);
}
