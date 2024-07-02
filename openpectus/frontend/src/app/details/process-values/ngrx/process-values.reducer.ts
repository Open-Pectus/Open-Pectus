import { createReducer } from '@ngrx/store';

export type ProcessValuesState = object;

const initialState: ProcessValuesState = {};

const reducer = createReducer(initialState,
);

export const processValuesSlice = {name: 'processValues', reducer};
