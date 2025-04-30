import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { switchMap } from 'rxjs';
import { secureRoutes } from './auth-config-loader.factory';

export const identityInterceptor: HttpInterceptorFn = (req, next) => {
  const oidcSecurityService = inject(OidcSecurityService);
  if(!oidcSecurityService.authenticated().isAuthenticated) return next(req);
  if(!secureRoutes.some(secureRoute => req.url.startsWith(secureRoute))) return next(req);

  return oidcSecurityService.getIdToken().pipe(switchMap(idToken => {
    const newReq = req.clone({
      headers: req.headers.append('X-Identity', idToken),
    });
    return next(newReq);
  }));
};
