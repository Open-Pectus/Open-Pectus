import { DATE_PIPE_DEFAULT_OPTIONS, DatePipe, DecimalPipe } from '@angular/common';
import '@angular/common/locales/global/da';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { isDevMode, LOCALE_ID, provideExperimentalZonelessChangeDetection } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { provideAnimations } from '@angular/platform-browser/animations';
import { PreloadAllModules, provideRouter, withPreloading } from '@angular/router';
import { provideServiceWorker } from '@angular/service-worker';
import { provideEffects } from '@ngrx/effects';
import { provideRouterStore, RouterState } from '@ngrx/router-store';
import { provideStore, Store } from '@ngrx/store';
import { provideStoreDevtools } from '@ngrx/store-devtools';
import { provideAuth, StsConfigLoader } from 'angular-auth-oidc-client';
import { setupWorker } from 'msw/browser';
import { provideToastr } from 'ngx-toastr';
import { AuthService } from './app/api';
import { AppComponent } from './app/app.component';
import { APP_ROUTES } from './app/app.routes';
import { authConfigLoaderFactory } from './app/auth/auth-config-loader.factory';
import { authInterceptor } from './app/auth/auth.interceptor';
import { Defaults } from './app/defaults';
import { DetailsActions } from './app/details/ngrx/details.actions';
import { metaReducers, reducers } from './app/ngrx';
import { AppEffects } from './app/ngrx/app.effects';
import { httpErrorInterceptor } from './app/shared/interceptors/http-error.interceptor';
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
    provideRouter(APP_ROUTES, withPreloading(PreloadAllModules)),
    provideAnimations(),
    provideToastr({
      progressBar: true,
      progressAnimation: 'increasing',
      tapToDismiss: false,
      closeButton: true,
    }),
    provideAuth({
      loader: {
        provide: StsConfigLoader,
        useFactory: authConfigLoaderFactory,
        deps: [AuthService, Store],
      },
    }),
    provideHttpClient(withInterceptors([httpErrorInterceptor, authInterceptor])),
    {provide: LOCALE_ID, useValue: 'da-DK'},
    DatePipe,
    DecimalPipe,
    ProcessValuePipe,
    {provide: DATE_PIPE_DEFAULT_OPTIONS, useValue: {dateFormat: Defaults.dateFormat}},
    provideServiceWorker('ngsw-worker.js', {
      enabled: !isDevMode(),
      registrationStrategy: 'registerWhenStable:30000',
    }),
  ],
})
  .catch(err => console.error(err)));
