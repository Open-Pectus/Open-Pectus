import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { filter, map, mergeMap, of, switchMap, take } from 'rxjs';
import { ProcessUnitService, VersionService } from '../api';
import { PubSubService } from '../shared/pub-sub.service';
import { AppActions } from './app.actions';
import { AppSelectors } from './app.selectors';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class AppEffects {
  fetchAuthConfigAtStart = createEffect(() => this.actions.pipe(
    ofType(AppActions.pageInitialized),
    switchMap(() => this.oidcSecurityService.getConfiguration()),
  ), {dispatch: false});

  storeUserData = createEffect(() => this.actions.pipe(
    ofType(AppActions.pageInitialized),
    switchMap(() => this.oidcSecurityService.userData$.pipe(
      map(userData => AppActions.userDataLoaded(userData)),
    )),
  ));

  storeUserId = createEffect(() => this.actions.pipe(
    ofType(AppActions.finishedAuthentication),
    switchMap(({isAuthenticated}) => {
      const userIdFromToken = this.oidcSecurityService.getPayloadFromIdToken().pipe<string>(map(payload => payload.oid));
      const userId = isAuthenticated ? userIdFromToken : of(crypto.randomUUID());
      return userId.pipe(map(userId => AppActions.userIdLoaded({userId})));
    }),
  ));

  checkAuthenticationIfEnabled = createEffect(() => this.actions.pipe(
    ofType(AppActions.authEnablementFetched),
    take(1),
    switchMap(({authIsEnabled}) => {
      if(!authIsEnabled) return of(AppActions.finishedAuthentication({isAuthenticated: false}));
      return this.oidcSecurityService.checkAuth().pipe(
        map(loginResponse => AppActions.finishedAuthentication({isAuthenticated: loginResponse.isAuthenticated})),
      );
    }),
  ));

  loadProcessUnitsOnPageInitialization = createEffect(() => this.actions.pipe(
    ofType(AppActions.finishedAuthentication),
    switchMap(() => {
      return this.processUnitService.getUnits().pipe(
        map(processUnits => AppActions.processUnitsLoaded({processUnits})),
      );
    }),
  ));

  loadBuildInfoPageInitialization = createEffect(() => this.actions.pipe(
    ofType(AppActions.finishedAuthentication),
    switchMap(() => {
      return this.versionService.getBuildInfo().pipe(
        map(buildInfo => AppActions.buildInfoLoaded({buildInfo})),
      );
    }),
  ));

  fetchUserPictureWhenAuthenticated = createEffect(() => this.actions.pipe(
    ofType(AppActions.finishedAuthentication),
    filter(({isAuthenticated}) => isAuthenticated),
    switchMap(() => {
      return this.httpClient.get('https://graph.microsoft.com/beta/me/photos/48x48/$value', {responseType: 'blob'});
    }),
    map(blob => {
      return AppActions.userPictureLoaded({userPicture: URL.createObjectURL(blob)});
    }),
  ));

  subscribeForUpdatesFromBackend = createEffect(() => this.actions.pipe(
    ofType(AppActions.finishedAuthentication),
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

  subscribeDeadManSwitch = createEffect(() => this.actions.pipe(
    ofType(AppActions.userIdLoaded, AppActions.websocketReconnected),
    concatLatestFrom(() => this.store.select(AppSelectors.userId)),
    map(([_, userId]) => {
      if(userId === undefined) return;
      this.pubSubService.subscribeDeadManSwitch(userId).subscribe();
    }),
  ), {dispatch: false});

  constructor(private actions: Actions,
              private store: Store,
              private processUnitService: ProcessUnitService,
              private pubSubService: PubSubService,
              private versionService: VersionService,
              private httpClient: HttpClient,
              private oidcSecurityService: OidcSecurityService) {}
}
