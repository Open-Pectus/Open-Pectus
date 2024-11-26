import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { mergeMap } from 'rxjs';

export const identityInterceptor: HttpInterceptorFn = (req, next) => {
  const oidcSecurityService = inject(OidcSecurityService);
  const secureRoutes = oidcSecurityService.getConfigurations().flatMap(config => config.secureRoutes ?? []);

  if(!oidcSecurityService.authenticated().isAuthenticated) return next(req);
  if(!secureRoutes.some(secureRoute => req.url.startsWith(secureRoute))) return next(req);
  
  return oidcSecurityService.getIdToken().pipe(mergeMap(idToken => {
    const newReq = req.clone({
      headers: req.headers.append('X-Identity', idToken),
    });
    return next(newReq);
  }));
};
