import { createReducer } from '@ngrx/store';

export interface ProcessValuesState {
}

const initialState: ProcessValuesState = {};

const reducer = createReducer(initialState,
);

export const processValuesSlice = {name: 'processValues', reducer};
