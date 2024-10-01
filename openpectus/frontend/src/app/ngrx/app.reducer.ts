import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { ProcessUnit } from '../api';
import { AppActions } from './app.actions';

export const appFeatureKey = 'app';

export interface AppState {
  processUnits: ProcessUnit[];
  authIsEnabled?: boolean;
  webSocketIsDisconnected: boolean;
}

const initialState: AppState = {
  processUnits: [],
  webSocketIsDisconnected: false,
};

export const appReducer = createReducer(initialState,
  on(AppActions.processUnitsLoaded, (state, {processUnits}) => produce(state, draft => {
    draft.processUnits = processUnits;
  })),
  on(AppActions.authEnablementFetched, (state, {authIsEnabled}) => produce(state, draft => {
    draft.authIsEnabled = authIsEnabled;
  })),
  on(AppActions.websocketDisconnected, (state) => produce(state, draft => {
    draft.webSocketIsDisconnected = true;
  })),
  on(AppActions.websocketReconnected, (state) => produce(state, draft => {
    draft.webSocketIsDisconnected = false;
  })),
);

