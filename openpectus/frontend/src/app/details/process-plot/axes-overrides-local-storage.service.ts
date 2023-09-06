import { Injectable } from '@angular/core';
import { YAxesLimitsOverride } from './process-plot.types';

@Injectable({
  providedIn: 'root',
})
export class AxesOverridesLocalStorageService {
  readonly yAxesLimitsOverrideKey = 'yAxesLimitsOverride';
  readonly xAxisProcessValueNameKey = 'xAxisProcessValueName';

  constructor() { }

  storeYAxesLimitsOverride(yAxesLimitsOverride: YAxesLimitsOverride | undefined) {
    window.localStorage.setItem(this.yAxesLimitsOverrideKey, JSON.stringify(yAxesLimitsOverride));
  }

  getYAxesLimitsOverride() {
    const storedValue = window.localStorage.getItem(this.yAxesLimitsOverrideKey);
    if(storedValue === null) return undefined;
    return JSON.parse(storedValue) as YAxesLimitsOverride;
  }
}
