import { NgModule } from '@angular/core';
import { AuthModule, LogLevel } from 'angular-auth-oidc-client';
import { authCallbackUrlPart } from '../app-routing.module';
import { AuthCallbackComponent } from './auth-callback.component';


@NgModule({
  declarations: [
    AuthCallbackComponent,
  ],
  imports: [AuthModule.forRoot({
    config: {
      authority: 'https://login.microsoftonline.com/fdfed7bd-9f6a-44a1-b694-6e39c468c150/v2.0',
      authWellknownEndpointUrl: 'https://login.microsoftonline.com/common/v2.0',
      // authWellknownEndpointUrl: 'https://login.microsoftonline.com/fdfed7bd-9f6a-44a1-b694-6e39c468c150/oauth2/v2.0',
      redirectUrl: `${window.location.origin}/${authCallbackUrlPart}`,
      clientId: 'fc7355bb-a6be-493f-90a1-cf57063f7948',
      scope: 'openid profile offline_access', // 'openid profile offline_access ' + your scopes
      responseType: 'code',
      silentRenew: true,
      useRefreshToken: true,
      maxIdTokenIatOffsetAllowedInSeconds: 600,
      // issValidationOff: false,
      issValidationOff: true,
      autoUserInfo: true,
      customParamsAuthRequest: {
        prompt: 'select_account', // login, consent
      },
      logLevel: LogLevel.None,
    },
  })],
  exports: [
    AuthModule,
    AuthCallbackComponent,
  ],
})
export class AuthConfigModule {}
