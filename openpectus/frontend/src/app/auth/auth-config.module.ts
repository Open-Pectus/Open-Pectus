import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { AuthInterceptor, AuthModule, LogLevel, StsConfigHttpLoader, StsConfigLoader } from 'angular-auth-oidc-client';
import { map } from 'rxjs';
import { AuthConfig, AuthService } from '../api';
import { authCallbackUrlPart } from '../app-routing.module';
import { AuthCallbackComponent } from './auth-callback.component';

export const httpLoaderFactory = (authService: AuthService) => {
  const config = authService.getConfig().pipe(map((customConfig: AuthConfig) => {
      return {
        authority: customConfig.authority_url,
        clientId: customConfig.client_id,
        // authority: 'https://login.microsoftonline.com/fdfed7bd-9f6a-44a1-b694-6e39c468c150/v2.0',
        authWellknownEndpointUrl: 'https://login.microsoftonline.com/common/v2.0',
        // authWellknownEndpointUrl: 'https://login.microsoftonline.com/fdfed7bd-9f6a-44a1-b694-6e39c468c150/oauth2/v2.0',
        redirectUrl: `${window.location.origin}/${authCallbackUrlPart}`,
        // clientId: 'fc7355bb-a6be-493f-90a1-cf57063f7948',
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
        deps: [AuthService],
      },
    }),
    HttpClientModule,
  ],
  providers: [
    {provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true},
  ],
  exports: [
    AuthModule,
    AuthCallbackComponent,
  ],
})
export class AuthConfigModule {}
