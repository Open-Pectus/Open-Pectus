import { ActionReducerMap, MetaReducer } from '@ngrx/store';
import { isDevMode } from '@angular/core';
import { appFeatureKey, appReducer, AppState } from './app.reducer';
import { routerReducer, RouterState } from '@ngrx/router-store';

export interface State {
  [appFeatureKey]: AppState;
  router: RouterState,
}

export const reducers: ActionReducerMap<State | { router: RouterState }> = {
  [appFeatureKey]: appReducer,
  router: routerReducer,
};


export const metaReducers: MetaReducer<State | { router: RouterState }>[] = isDevMode() ? [] : [];
