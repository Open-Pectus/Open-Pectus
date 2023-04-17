import { ActionReducerMap, MetaReducer } from '@ngrx/store';
import { isDevMode } from '@angular/core';
import { appFeatureKey, appReducer, AppState } from './app.reducer';

export interface State {
  [appFeatureKey]: AppState;
}

export const reducers: ActionReducerMap<State> = {
  [appFeatureKey]: appReducer
};


export const metaReducers: MetaReducer<State>[] = isDevMode() ? [] : [];
