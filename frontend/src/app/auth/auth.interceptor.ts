import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Store } from '@ngrx/store';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { combineLatestWith, filter, identity, switchMap, take } from 'rxjs';
import { AppSelectors } from '../ngrx/app.selectors';
import { UtilMethods } from '../shared/util-methods';
import { secureRoutes } from './auth-config-loader.factory';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const oidcSecurityService = inject(OidcSecurityService);
  const store = inject(Store);
  const hasFinishedAuthentication = store.select(AppSelectors.hasFinishedAuthentication).pipe(filter(identity), take(1));
  const authIsEnabled = store.select(AppSelectors.authIsEnabled).pipe(filter(UtilMethods.isNotNullOrUndefined), take(1));
  // https://graph.microsoft.com/oidc/userinfo is used while running authentication check and should not be delayed.
  if(req.url === 'https://graph.microsoft.com/oidc/userinfo') return next(req);
  if(!secureRoutes.some(secureRoute => req.url.startsWith(secureRoute))) return next(req);

  return hasFinishedAuthentication.pipe(
    combineLatestWith(
      authIsEnabled,
      oidcSecurityService.getAccessToken(),
      oidcSecurityService.getIdToken(),
    ),
    switchMap(([_, authIsEnabled, accessToken, idToken]) => {
      if(!authIsEnabled) return next(req);
      req = req.clone({
        headers: req.headers.set('Authorization', 'Bearer ' + accessToken).set('X-Identity', idToken),
      });
      return next(req);
    }),
  );
};
