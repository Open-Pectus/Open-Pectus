import { isDevMode, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { StoreModule } from '@ngrx/store';
import { metaReducers, reducers } from './ngrx/';
import { PushModule } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { AppEffects } from './ngrx/app.effects';
import { RouterState, StoreRouterConnectingModule } from '@ngrx/router-store';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';
import { TestComponent } from './test.component';
import { ApiModule, Configuration } from './api';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  declarations: [
    AppComponent,
    TestComponent,
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
    PushModule,
    EffectsModule.forRoot([AppEffects]),
    StoreRouterConnectingModule.forRoot({routerState: RouterState.Minimal}),
    StoreDevtoolsModule.instrument({
      maxAge: 25,
      logOnly: !isDevMode(),
      actionsBlocklist: ['@ngrx'],
    }),
    ApiModule.forRoot(() => new Configuration({basePath: window.location.origin})),
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
