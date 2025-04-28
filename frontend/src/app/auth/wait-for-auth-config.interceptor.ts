import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Store } from '@ngrx/store';
import { filter, switchMap, take } from 'rxjs';
import { AppSelectors } from '../ngrx/app.selectors';

export const waitForAuthConfigInterceptor: HttpInterceptorFn = (req, next) => {
  const authIsEnabled = inject(Store).select(AppSelectors.authIsEnabled);
  return authIsEnabled.pipe(
    filter(authIsEnabled => authIsEnabled !== undefined || req.url === '/auth/config'),
    take(1),
    switchMap(() => next(req)),
  );
};
