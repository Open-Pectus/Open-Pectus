import { createFeatureSelector, createSelector } from '@ngrx/store';
import { format } from 'date-fns';
import { produce } from 'immer';
import { Defaults } from '../../../defaults';
import { runLogSlice, RunLogState } from './run-log.reducer';

export class RunLogSelectors {
  static selectFeature = createFeatureSelector<RunLogState>(runLogSlice.name);
  static filterText = createSelector(this.selectFeature, state => state.filterText);
  static onlyRunning = createSelector(this.selectFeature, state => state.onlyRunning);
  static runLog = createSelector(this.selectFeature, this.onlyRunning, this.filterText,
    (state, checked, filterText) => produce(state.runLog, draft => {
      if(checked) draft.lines = draft.lines.filter(line => line.end === undefined);
      if(filterText !== '') {
        draft.lines = draft.lines.filter(line => {
          return (line.end !== undefined && format(new Date(line.end), Defaults.dateFormat)?.includes(filterText)) ||
                 (line.start !== undefined && format(new Date(line.start), Defaults.dateFormat)?.includes(filterText)) ||
                 line.command.command.toLowerCase().includes(filterText.toLowerCase());
        });
      }
      draft.lines.sort((a, b) => new Date(a.start).valueOf() - new Date(b.start).valueOf());
    }));
  static expandedLines = createSelector(this.selectFeature, state => state.expandedLines);

  constructor() {}
}
