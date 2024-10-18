import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { map, mergeMap, switchMap } from 'rxjs';
import { ProcessUnitService, VersionService } from '../api';
import { PubSubService } from '../shared/pub-sub.service';
import { AppActions } from './app.actions';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class AppEffects {
  loadProcessUnitsOnPageInitialization = createEffect(() => this.actions.pipe(
    ofType(AppActions.pageInitialized),
    switchMap(() => {
      return this.processUnitService.getUnits().pipe(
        map(processUnits => AppActions.processUnitsLoaded({processUnits})),
      );
    }),
  ));

  loadBuildInfoPageInitialization = createEffect(() => this.actions.pipe(
    ofType(AppActions.pageInitialized),
    switchMap(() => {
      return this.versionService.getBuildInfo().pipe(
        map(buildInfo => AppActions.buildInfoLoaded({buildInfo})),
      );
    }),
  ));

  subscribeForUpdatesFromBackend = createEffect(() => this.actions.pipe(
    ofType(AppActions.pageInitialized),
    mergeMap(() => {
      return this.pubSubService.subscribeProcessUnits().pipe(
        map(_ => AppActions.processUnitsUpdatedOnBackend()),
      );
    }),
  ));

  fetchOnUpdateFromBackend = createEffect(() => this.actions.pipe(
    ofType(AppActions.processUnitsUpdatedOnBackend),
    mergeMap(() => {
      return this.processUnitService.getUnits().pipe(
        map(processUnits => AppActions.processUnitsLoaded({processUnits})),
      );
    }),
  ));

  constructor(private actions: Actions,
              private processUnitService: ProcessUnitService,
              private pubSubService: PubSubService,
              private versionService: VersionService) {}


}
