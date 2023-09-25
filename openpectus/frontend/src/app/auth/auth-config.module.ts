import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { Store } from '@ngrx/store';
import {
  AbstractSecurityStorage,
  AuthInterceptor,
  AuthModule,
  DefaultLocalStorageService,
  LogLevel,
  OpenIdConfiguration,
  StsConfigHttpLoader,
  StsConfigLoader,
} from 'angular-auth-oidc-client';
import { map } from 'rxjs';
import { AuthConfig, AuthService } from '../api';
import { authCallbackUrlPart } from '../app-routing.module';
import { AppActions } from '../ngrx/app.actions';
import { AuthCallbackComponent } from './auth-callback.component';

export const httpLoaderFactory = (authService: AuthService, store: Store) => {
  const config = authService.getConfig().pipe<OpenIdConfiguration>(map((customConfig: AuthConfig) => {
      store.dispatch(AppActions.authEnablementFetched({authIsEnabled: customConfig.use_auth}));
      if(!customConfig.use_auth) {
        return {
          authority: window.location.origin,
          clientId: 'DUMMY',
          redirectUrl: `${window.location.origin}/${authCallbackUrlPart}`,
        };
      }
      return {
        authority: customConfig.authority_url,
        clientId: customConfig.client_id,
        authWellknownEndpointUrl: 'https://login.microsoftonline.com/common/v2.0',
        redirectUrl: `${window.location.origin}/${authCallbackUrlPart}`,
        scope: 'openid profile offline_access', // 'openid profile offline_access ' + your scopes
        responseType: 'code',
        silentRenew: true,
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
        secureRoutes: [`/api/`],
      };
    }),
  );

  return new StsConfigHttpLoader(config);
};


@NgModule({
  declarations: [
    AuthCallbackComponent,
  ],
  imports: [
    AuthModule.forRoot({
      loader: {
        provide: StsConfigLoader,
        useFactory: httpLoaderFactory,
        deps: [AuthService, Store],
      },
    }),
    HttpClientModule,
  ],
  providers: [
    {provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true},
    {provide: AbstractSecurityStorage, useClass: DefaultLocalStorageService},
  ],
  exports: [
    AuthModule,
    AuthCallbackComponent,
  ],
})
export class AuthConfigModule {}