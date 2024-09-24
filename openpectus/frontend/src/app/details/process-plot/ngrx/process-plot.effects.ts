import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { map, of, switchMap } from 'rxjs';
import { ProcessUnitService, RecentRunsService } from '../../../api';
import { AxesOverridesLocalStorageService } from '../axes-overrides-local-storage.service';
import { ProcessPlotActions } from './process-plot.actions';
import { ProcessPlotSelectors } from './process-plot.selectors';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class ProcessPlotEffects {
  fetchPlotConfigurationOnComponentInitializationForUnit = createEffect(() => this.actions.pipe(
    ofType(ProcessPlotActions.processPlotComponentInitializedForUnit),
    switchMap(({unitId}) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getPlotConfiguration({unitId}).pipe(
        map(configuration => ProcessPlotActions.plotConfigurationFetched({configuration})));
    }),
  ));

  fetchPlotConfigurationOnComponentInitializationForRecentRun = createEffect(() => this.actions.pipe(
    ofType(ProcessPlotActions.processPlotComponentInitializedForRecentRun),
    switchMap(({recentRunId}) => {
      if(recentRunId === undefined) return of();
      return this.recentRunsService.getRecentRunPlotConfiguration({runId: recentRunId}).pipe(
        map(configuration => ProcessPlotActions.plotConfigurationFetched({configuration})));
    }),
  ));

  fetchPlotLogOnComponentInitializationForUnit = createEffect(() => this.actions.pipe(
    ofType(ProcessPlotActions.processPlotComponentInitializedForUnit),
    switchMap(({unitId}) => {
      if(unitId === undefined) return of();
      return this.processUnitService.getPlotLog({unitId}).pipe(
        map(plotLog => ProcessPlotActions.plotLogFetched({plotLog})));
    }),
  ));

  fetchPlotLogOnComponentInitializationForRecentRun = createEffect(() => this.actions.pipe(
    ofType(ProcessPlotActions.processPlotComponentInitializedForRecentRun),
    switchMap(({recentRunId}) => {
      if(recentRunId === undefined) return of();
      return this.recentRunsService.getRecentRunPlotLog({runId: recentRunId}).pipe(
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
              private axesOverridesLocalStorageService: AxesOverridesLocalStorageService,
              private recentRunsService: RecentRunsService) {}
}
