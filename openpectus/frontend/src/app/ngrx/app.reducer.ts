import { createReducer } from '@ngrx/store';

export const appFeatureKey = 'app';

export interface AppState {
}

const initialState: AppState = {};

export const appReducer = createReducer(initialState,
);

