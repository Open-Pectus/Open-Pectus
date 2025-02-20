import { DATE_PIPE_DEFAULT_OPTIONS, DatePipe, DecimalPipe } from '@angular/common';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import '@angular/common/locales/global/da';
import { importProvidersFrom, isDevMode, LOCALE_ID, provideExperimentalZonelessChangeDetection } from '@angular/core';
import { bootstrapApplication, BrowserModule } from '@angular/platform-browser';
import { provideRouter } from '@angular/router';
import { LetDirective, PushPipe } from '@ngrx/component';
import { provideEffects } from '@ngrx/effects';
import { provideRouterStore, RouterState } from '@ngrx/router-store';
import { provideStore } from '@ngrx/store';
import { provideStoreDevtools } from '@ngrx/store-devtools';
import { setupWorker } from 'msw/browser';
import { AppComponent } from './app/app.component';
import { APP_ROUTES } from './app/app.routes';
import { AuthConfigModule } from './app/auth/auth-config.module';
import { Defaults } from './app/defaults';
import { DetailsActions } from './app/details/ngrx/details.actions';
import { metaReducers, reducers } from './app/ngrx';
import { AppEffects } from './app/ngrx/app.effects';
import { ProcessValuePipe } from './app/shared/pipes/process-value.pipe';

import { handlers } from './msw/handlers';
import { MswEnablement } from './msw/msw-enablement';

async function enableMocking() {
  if(!MswEnablement.isEnabled) return;
  const worker = setupWorker(...handlers);
  return worker.start({
    quiet: true,
    onUnhandledRequest: (request: Request) => {
      const url = new URL(request.url);
      const pathname = url.pathname;
      if(pathname.startsWith('/assets')
         || pathname.startsWith('/node_modules')
         || pathname.startsWith('/src')
         || pathname.startsWith('/api/trigger-publish-msw')
         || pathname.endsWith('.ico')
         || pathname.endsWith('.js')
         || pathname.endsWith('.json')
         || pathname.endsWith('.ttf')
         || pathname.endsWith('.wasm')
         || pathname.startsWith('/@fs')
         || url.host !== window.location.host
      ) {
        return;
      }
      console.warn(`url ${request.url} was not mocked by MSW`);
    },
  });
}

enableMocking().then(() => bootstrapApplication(AppComponent, {
  providers: [
    provideExperimentalZonelessChangeDetection(),
    provideStore(reducers, {
      metaReducers,
      runtimeChecks: {
        strictStateImmutability: true,
        strictActionImmutability: true,
        // strictStateSerializability: true,
        // strictActionSerializability: true,
        // strictActionWithinNgZone: true,
        strictActionTypeUniqueness: true,
      },
    }),
    provideEffects([AppEffects]),
    provideRouterStore({routerState: RouterState.Minimal}),
    provideStoreDevtools({
      maxAge: 50,
      logOnly: !isDevMode(),
      actionsBlocklist: [
        '@ngrx',
        DetailsActions.processValuesFetched.type,
        // RunLogActions.runLogPolledForUnit.type,
        // DetailsActions.controlStateFetched.type,
        // MethodEditorActions.methodPolledForUnit.type,
      ],
    }),
    provideRouter(APP_ROUTES),
    importProvidersFrom(
      BrowserModule,
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
  .catch(err => console.error(err)));
