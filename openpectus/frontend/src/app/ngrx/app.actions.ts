import { createAction, props } from '@ngrx/store';
import { ProcessUnit } from '../api/models/ProcessUnit';

const source = '[App] ';

export class AppActions {
  static pageInitialized = createAction(source + 'Page initialized');
  static processUnitsLoaded = createAction(source + 'Process Units Loaded', props<{ processUnits: ProcessUnit[] }>());
  static authEnablementFetched = createAction(source + 'Auth Enablement Fetched', props<{ authIsEnabled: boolean }>());
  static processUnitsUpdatedOnBackend = createAction(source + 'Process Units Updated On Backend');
  static websocketDisconnected = createAction(source + 'Websocket Disconnected');
  static websocketReconnected = createAction(source + 'Websocket Reconnected');
}
