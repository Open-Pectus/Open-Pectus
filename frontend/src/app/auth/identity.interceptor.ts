import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Store } from '@ngrx/store';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { filter, switchMap, take } from 'rxjs';
import { AppSelectors } from '../ngrx/app.selectors';
import { secureRoutes } from './auth-config-loader.factory';

export const identityInterceptor: HttpInterceptorFn = (req, next) => {
  const hasFinishedAuthentication = inject(Store).select(AppSelectors.hasFinishedAuthentication);
  const oidcSecurityService = inject(OidcSecurityService);
  if(!oidcSecurityService.authenticated().isAuthenticated) return next(req);
  if(!secureRoutes.some(secureRoute => req.url.startsWith(secureRoute))) return next(req);

  return hasFinishedAuthentication.pipe(
    filter(hasFinishedAuthentication => hasFinishedAuthentication),
    take(1),
    switchMap(() => oidcSecurityService.getIdToken().pipe(switchMap(idToken => {
        const newReq = req.clone({
          headers: req.headers.append('X-Identity', idToken),
        });
        return next(newReq);
      })),
    ),
  );
};
