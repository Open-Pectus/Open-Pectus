import { createFeatureSelector, createSelector } from '@ngrx/store';
import { methodEditorSlice, MethodEditorState } from './method-editor.reducer';

export class MethodEditorSelectors {
  static selectFeature = createFeatureSelector<MethodEditorState>(methodEditorSlice.name);
  static monacoServicesInitialized = createSelector(this.selectFeature, state => state.monacoServicesInitialized);
  static isDirty = createSelector(this.selectFeature, state => state.isDirty);
  static method = createSelector(this.selectFeature, state => state.method);
  static methodState = createSelector(this.selectFeature, state => state.methodState);
  static methodLines = createSelector(this.method, method => method.lines);
  static methodContent = createSelector(this.methodLines, methodLines => methodLines.map(line => line.content).join('\n'));
  static lineIds = createSelector(this.methodLines, methodLines => methodLines.map(line => line.id));
  static injectedLineIds = createSelector(this.methodState, methodState => methodState.injected_line_ids);
  static executedLineIds = createSelector(this.methodState, methodState => methodState.executed_line_ids);
  static startedLineIds = createSelector(this.methodState, methodState => methodState.started_line_ids);
}
