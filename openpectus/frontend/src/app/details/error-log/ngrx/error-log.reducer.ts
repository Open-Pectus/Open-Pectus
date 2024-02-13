import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { ErrorLog } from '../../../api';
import { ErrorLogActions } from './error-log.actions';

export interface ErrorLogState {
  errorLog: ErrorLog;
}

const initialState: ErrorLogState = {
  errorLog: {entries: []},
};

const reducer = createReducer(initialState,
  on(ErrorLogActions.errorLogComponentDestroyed, () => initialState),
  on(ErrorLogActions.errorLogFetched, (state, {errorLog}) => produce(state, draft => {
    draft.errorLog = errorLog;
  })),
);

export const errorLogSlice = {name: 'errorLog', reducer};
