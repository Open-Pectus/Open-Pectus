import { createFeatureSelector, createSelector } from '@ngrx/store';
import { format } from 'date-fns';
import { produce } from 'immer';
import { runLogSlice, RunLogState } from './run-log.reducer';

export class RunLogSelectors {
  static selectFeature = createFeatureSelector<RunLogState>(runLogSlice.name);
  static filterText = createSelector(this.selectFeature, state => state.filterText);
  static onlyRunning = createSelector(this.selectFeature, state => state.onlyRunning);
  static dateFormat = createSelector(this.selectFeature, state => state.dateFormat);
  static runLog = createSelector(this.selectFeature, this.onlyRunning, this.filterText, this.dateFormat,
    (state, checked, filterText, dateFormat) => produce(state.runLog, draft => {
      if(checked) draft.lines = draft.lines.filter(line => line.end === undefined);
      if(filterText !== '') {
        draft.lines = draft.lines.filter(line => {
          console.log(format(new Date(line.start), dateFormat));
          return (line.end !== undefined && format(new Date(line.end), dateFormat)?.includes(filterText)) ||
                 (line.start !== undefined && format(new Date(line.start), dateFormat)?.includes(filterText)) ||
                 line.command.command.toLowerCase().includes(filterText.toLowerCase());
        });
      }
      draft.lines.sort((a, b) => new Date(a.start).valueOf() - new Date(b.start).valueOf());
    }));

  constructor() {}
}
