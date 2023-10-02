import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { map, of, switchMap } from 'rxjs';
import { ProcessUnitService } from '../../../api';
import { selectRouteParam } from '../../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../../details-routing-url-parts';
import { AxesOverridesLocalStorageService } from '../axes-overrides-local-storage.service';
import { ProcessPlotActions } from './process-plot.actions';
import { ProcessPlotSelectors } from './process-plot.selectors';

@Injectable()
export class ProcessPlotEffects {
  fetchPlotConfigurationOnComponentInitialization = createEffect(() => this.actions.pipe(
    ofType(ProcessPlotActions.processPlotComponentInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, id]) => {
      if(id === undefined) return of();
      return this.processUnitService.getPlotConfiguration(id).pipe(
        map(configuration => ProcessPlotActions.plotConfigurationFetched({configuration})));
    }),
  ));

  fetchPlotLogOnComponentInitialization = createEffect(() => this.actions.pipe(
    ofType(ProcessPlotActions.processPlotComponentInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, id]) => {
      if(id === undefined) return of();
      return this.processUnitService.getPlotLog(id).pipe(
        map(plotLog => ProcessPlotActions.plotLogFetched({plotLog})));
    }),
  ));

  saveYAxesLimitOverrideInLocalStorage = createEffect(() => this.actions.pipe(
    ofType(ProcessPlotActions.yOverrideDialogSaveClicked, ProcessPlotActions.processPlotReset),
    concatLatestFrom(() => this.store.select(ProcessPlotSelectors.yAxesLimitsOverride)),
    switchMap(([_, yOverrideLimits]) => {
      this.axesOverridesLocalStorageService.storeYAxesLimitsOverride(yOverrideLimits);
      return of();
    }),
  ), {dispatch: false});

  restoreYAxesLimitsOverrideFromLocalStorage = createEffect(() => this.actions.pipe(
    ofType(ProcessPlotActions.processPlotInitialized),
    switchMap(() => {
      const storedValue = this.axesOverridesLocalStorageService.getYAxesLimitsOverride();
      if(storedValue === undefined) return of();
      return of(ProcessPlotActions.yAxesOverrideLimitsRestoredFromLocalStorage({yAxesLimitsOverride: storedValue}));
    }),
  ));

  saveXAxisProcessValueNameInLocalStorage = createEffect(() => this.actions.pipe(
    ofType(ProcessPlotActions.xOverrideDialogSaveClicked, ProcessPlotActions.processPlotReset),
    concatLatestFrom(() => this.store.select(ProcessPlotSelectors.xAxisProcessValueOverride)),
    switchMap(([_, xAxisProcessValueName]) => {
      this.axesOverridesLocalStorageService.storeXAxisProcessValueName(xAxisProcessValueName);
      return of();
    }),
  ), {dispatch: false});

  restoreXAxisProcessValueNameFromLocalStorage = createEffect(() => this.actions.pipe(
    ofType(ProcessPlotActions.processPlotInitialized),
    switchMap(() => {
      const storedValue = this.axesOverridesLocalStorageService.getXAxisProcessValueName();
      if(storedValue === undefined) return of();
      return of(ProcessPlotActions.xAxisProcessValueNameRestoredFromLocalStorage({xAxisProcessValueName: storedValue}));
    }),
  ));

  constructor(private actions: Actions,
              private store: Store,
              private processUnitService: ProcessUnitService,
              private axesOverridesLocalStorageService: AxesOverridesLocalStorageService) {}
}
