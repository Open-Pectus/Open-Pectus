import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Store } from '@ngrx/store';
import { filter, switchMap, take } from 'rxjs';
import { AppSelectors } from '../ngrx/app.selectors';

export const waitForAuthInterceptor: HttpInterceptorFn = (req, next) => {
  const hasFinishedAuthentication = inject(Store).select(AppSelectors.hasFinishedAuthentication);
  if(!req.url.startsWith('/api/')) return next(req);
  return hasFinishedAuthentication.pipe(
    filter(hasFinishedAuthentication => hasFinishedAuthentication),
    take(1),
    switchMap(() => next(req)),
  );
};
