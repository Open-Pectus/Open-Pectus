import { DATE_PIPE_DEFAULT_OPTIONS, DatePipe, DecimalPipe } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import '@angular/common/locales/global/da';
import { isDevMode, LOCALE_ID, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { LetDirective, PushPipe } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { RouterState, StoreRouterConnectingModule } from '@ngrx/router-store';
import { StoreModule } from '@ngrx/store';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AuthConfigModule } from './auth/auth-config.module';
import { Defaults } from './defaults';
import { MswEnablementComponent } from './msw-enablement.component';
import { metaReducers, reducers } from './ngrx/';
import { AppEffects } from './ngrx/app.effects';
import { ProcessValuePipe } from './shared/pipes/process-value.pipe';
import { TopBarComponent } from './top-bar.component';


@NgModule({
  declarations: [
    AppComponent,
    TopBarComponent,
    MswEnablementComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    StoreModule.forRoot(reducers, {
      metaReducers,
      runtimeChecks: {
        strictStateImmutability: true,
        strictActionImmutability: true,
        strictStateSerializability: true,
        strictActionSerializability: true,
        strictActionWithinNgZone: true,
        strictActionTypeUniqueness: true,
      },
    }),
    EffectsModule.forRoot([AppEffects]),
    StoreRouterConnectingModule.forRoot({routerState: RouterState.Minimal}),
    StoreDevtoolsModule.instrument({
      maxAge: 50,
      logOnly: !isDevMode(),
      actionsBlocklist: [
        '@ngrx',
        // DetailsActions.processValuesFetched.type,
        // RunLogActions.runLogPolledForUnit.type,
        // DetailsActions.controlStateFetched.type,
        // MethodEditorActions.methodPolledForUnit.type,
      ],
    }),
    AuthConfigModule,
    PushPipe,
    LetDirective,
  ],
  providers: [
    {provide: LOCALE_ID, useValue: 'da-DK'},
    DatePipe,
    DecimalPipe,
    ProcessValuePipe,
    {provide: DATE_PIPE_DEFAULT_OPTIONS, useValue: {dateFormat: Defaults.dateFormat}},
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
