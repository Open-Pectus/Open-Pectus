import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Store } from '@ngrx/store';
import { filter, switchMap, take } from 'rxjs';
import { AppSelectors } from '../ngrx/app.selectors';
import { secureRoutes } from './auth-config-loader.factory';

export const waitForAuthInterceptor: HttpInterceptorFn = (req, next) => {
  const hasFinishedAuthentication = inject(Store).select(AppSelectors.hasFinishedAuthentication);
  // https://graph.microsoft.com/oidc/userinfo is used while running authentication check and should not be delayed.
  if(req.url === 'https://graph.microsoft.com/oidc/userinfo') return next(req);
  if(!secureRoutes.some(secureRoute => req.url.startsWith(secureRoute))) return next(req);
  return hasFinishedAuthentication.pipe(
    filter(hasFinishedAuthentication => hasFinishedAuthentication),
    take(1),
    switchMap(() => next(req)),
  );
};
