import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { AggregatedErrorLog } from '../../api';
import { DetailsActions } from './details.actions';

export interface DetailsState {
  allProcessValues: boolean;
  errorLog: AggregatedErrorLog;
}

const initialState: DetailsState = {
  allProcessValues: false,
  errorLog: {entries: []},
};

const reducer = createReducer(initialState,
  on(DetailsActions.unitDetailsInitialized, state => produce(state, draft => {
    draft.allProcessValues = false;
  })),
  on(DetailsActions.toggleAllProcessValues, (state, {allProcessValues}) => produce(state, draft => {
    draft.allProcessValues = allProcessValues;
  })),
);

export const detailsSlice = {name: 'details', reducer};
