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
    if(yAxesLimitsOverride === undefined) {
      window.localStorage.removeItem(this.yAxesLimitsOverrideKey);
    } else {
      window.localStorage.setItem(this.yAxesLimitsOverrideKey, JSON.stringify(yAxesLimitsOverride));
    }
  }

  getYAxesLimitsOverride() {
    const storedValue = window.localStorage.getItem(this.yAxesLimitsOverrideKey);
    if(storedValue === null) return undefined;
    return JSON.parse(storedValue) as YAxesLimitsOverride;
  }

  storeXAxisProcessValueName(xAxisProcessValueName: string | undefined) {
    if(xAxisProcessValueName === undefined) {
      window.localStorage.removeItem(this.xAxisProcessValueNameKey);
    } else {
      window.localStorage.setItem(this.xAxisProcessValueNameKey, JSON.stringify(xAxisProcessValueName));
    }
  }

  getXAxisProcessValueName() {
    const storedValue = window.localStorage.getItem(this.xAxisProcessValueNameKey);
    if(storedValue === null) return undefined;
    return JSON.parse(storedValue) as string | undefined;
  }
}
