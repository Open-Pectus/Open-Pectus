import { Store } from '@ngrx/store';
import { LogLevel, OpenIdConfiguration, StsConfigHttpLoader } from 'angular-auth-oidc-client';
import { map, shareReplay } from 'rxjs';
import { tap } from 'rxjs/operators';
import { AuthConfig, AuthService } from '../api';
import { authCallbackUrlPart } from '../app.routes';
import { AppActions } from '../ngrx/app.actions';

export const secureRoutes = [`/api/`, `https://graph.microsoft.com/`];

export const authConfigLoaderFactory = (authService: AuthService, store: Store) => {
  const config = authService.getConfig().pipe(
    tap((customConfig: AuthConfig) => store.dispatch(AppActions.authEnablementFetched({authIsEnabled: customConfig.use_auth}))),
    map((customConfig: AuthConfig) => {
      if(!customConfig.use_auth) {
        return {
          authority: window.location.origin,
          clientId: 'DUMMY',
          redirectUrl: `${window.location.origin}/${authCallbackUrlPart}`,
        } satisfies OpenIdConfiguration;
      }
      return {
        authority: customConfig.authority_url,
        clientId: customConfig.client_id,
        authWellknownEndpointUrl: customConfig.well_known_url,
        redirectUrl: `${window.location.origin}/${authCallbackUrlPart}`,
        scope: 'openid profile offline_access User.Read', // 'openid profile offline_access ' + your scopes
        responseType: 'code',
        silentRenew: true,
        renewTimeBeforeTokenExpiresInSeconds: 60,
        tokenRefreshInSeconds: 60,
        useRefreshToken: true,
        maxIdTokenIatOffsetAllowedInSeconds: 600, // 600, i.e. 10 minutes, is the default generated value.
        ignoreNonceAfterRefresh: true,
        // issValidationOff: false, // should be enabled when possible (using single-tenant Azure AD).
        issValidationOff: true,
        autoUserInfo: true,
        // customParamsAuthRequest: {
        //   prompt: 'select_account', // login, consent
        // },
        logLevel: LogLevel.None,
        secureRoutes: secureRoutes,
      } satisfies OpenIdConfiguration;
    }),
    shareReplay(1),
  );

  return new StsConfigHttpLoader(config);
};
