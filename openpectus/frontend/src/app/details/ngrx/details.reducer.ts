import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { ErrorLog } from '../../api/models/ErrorLog';
import { RecentRun } from '../../api/models/RecentRun';
import { DetailsActions } from './details.actions';

export interface DetailsState {
  allProcessValues: boolean;
  recentRun?: RecentRun;
  errorLog: ErrorLog;
}

const initialState: DetailsState = {
  allProcessValues: false,
  errorLog: {entries: []},
};

const reducer = createReducer(initialState,
  on(DetailsActions.unitDetailsInitialized, state => produce(state, draft => {
    draft.allProcessValues = false;
  })),
  on(DetailsActions.recentRunFetched, (state, {recentRun}) => produce(state, draft => {
    draft.recentRun = recentRun;
  })),
  on(DetailsActions.toggleAllProcessValues, (state, {allProcessValues}) => produce(state, draft => {
    draft.allProcessValues = allProcessValues;
  })),
);

export const detailsSlice = {name: 'details', reducer};
