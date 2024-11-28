import { createAction, props } from '@ngrx/store';
import { BuildInfo, ProcessUnit } from '../api';
import { UserData } from './app.reducer';

const source = '[App] ';

export class AppActions {
  static pageInitialized = createAction(source + 'Page initialized');
  static processUnitsLoaded = createAction(source + 'Process Units Loaded', props<{ processUnits: ProcessUnit[] }>());
  static authEnablementFetched = createAction(source + 'Auth Enablement Fetched', props<{ authIsEnabled: boolean }>());
  static processUnitsUpdatedOnBackend = createAction(source + 'Process Units Updated On Backend');
  static websocketDisconnected = createAction(source + 'Websocket Disconnected');
  static websocketReconnected = createAction(source + 'Websocket Reconnected');
  static buildInfoLoaded = createAction(source + 'Build Info Loaded', props<{ buildInfo: BuildInfo }>());
  static finishedAuthentication = createAction(source + 'Finished Authentication', props<{ isAuthenticated: boolean }>());
  static userDataLoaded = createAction(source + 'User Data Loaded', props<{ userData: UserData }>());
  static userPictureLoaded = createAction(source + 'User Picture Loaded', props<{ userPicture: string }>());
}
