import { createReducer, on } from '@ngrx/store';
import { produce } from 'immer';
import { BuildInfo, ProcessUnit } from '../api';
import { AppActions } from './app.actions';

export const appFeatureKey = 'app';

export interface UserData {
  sub: string;
  name: string;
  family_name: string;
  given_name: string;
  picture: string;
  email: string;
}

export interface AppState {
  processUnits: ProcessUnit[];
  authIsEnabled?: boolean;
  webSocketIsDisconnected: boolean;
  buildInfo?: BuildInfo;
  userData?: UserData;
  userPicture?: string;
  hasFinishedAuthentication: boolean;
}

const initialState: AppState = {
  processUnits: [],
  webSocketIsDisconnected: false,
  hasFinishedAuthentication: false,
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
  on(AppActions.buildInfoLoaded, (state, {buildInfo}) => produce(state, draft => {
    draft.buildInfo = buildInfo;
  })),
  on(AppActions.userDataLoaded, (state, {userData}) => produce(state, draft => {
    draft.userData = userData;
  })),
  on(AppActions.userPictureLoaded, (state, {userPicture}) => produce(state, draft => {
    draft.userPicture = userPicture;
  })),
  on(AppActions.finishedAuthentication, state => produce(state, draft => {
    draft.hasFinishedAuthentication = true;
  })),
);

