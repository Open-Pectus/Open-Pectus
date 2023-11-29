import { DATE_PIPE_DEFAULT_OPTIONS, DatePipe, DecimalPipe } from '@angular/common';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { importProvidersFrom, isDevMode, LOCALE_ID } from '@angular/core';
import { bootstrapApplication, BrowserModule } from '@angular/platform-browser';
import { LetDirective, PushPipe } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { RouterState, StoreRouterConnectingModule } from '@ngrx/router-store';
import { StoreModule } from '@ngrx/store';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';
import { setupWorker } from 'msw/browser';
import { AppRoutingModule } from './app/app-routing.module';
import { AppComponent } from './app/app.component';
import { AuthConfigModule } from './app/auth/auth-config.module';
import { Defaults } from './app/defaults';
import { metaReducers, reducers } from './app/ngrx';
import { AppEffects } from './app/ngrx/app.effects';
import { ProcessValuePipe } from './app/shared/pipes/process-value.pipe';

import { handlers } from './msw/handlers';
import { MswEnablement } from './msw/msw-enablement';

if(MswEnablement.isEnabled) {
  const worker = setupWorker(...handlers);
  await worker.start({
    onUnhandledRequest: (request: Request) => {
      const url = new URL(request.url);
      const pathname = url.pathname;
      if(pathname.startsWith('/assets')
         || pathname.startsWith('/node_modules')
         || pathname.startsWith('/src')
         || pathname.startsWith('/api/trigger-pubsub')
         || pathname.endsWith('.ico')
         || pathname.endsWith('.js')
         || pathname.endsWith('.json')
         || pathname.endsWith('.ttf')
         || pathname.endsWith('.wasm')
         || url.host !== window.location.host
      ) {
        return;
      }
      console.warn(`url ${request.url} was not mocked by MSW`);
    },
  });
}

bootstrapApplication(AppComponent, {
  providers: [
    importProvidersFrom(
      BrowserModule,
      AppRoutingModule,
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
      EffectsModule.forRoot([AppEffects]), StoreRouterConnectingModule.forRoot({routerState: RouterState.Minimal}),
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
    ),
    {provide: LOCALE_ID, useValue: 'da-DK'},
    DatePipe,
    DecimalPipe,
    ProcessValuePipe,
    {provide: DATE_PIPE_DEFAULT_OPTIONS, useValue: {dateFormat: Defaults.dateFormat}},
    provideHttpClient(withInterceptorsFromDi()),
  ],
})
  .catch(err => console.error(err));
