import { inject } from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { Store } from '@ngrx/store';
import { AutoLoginPartialRoutesGuard } from 'angular-auth-oidc-client';
import { mergeMap, of, take } from 'rxjs';
import { AppSelectors } from '../ngrx/app.selectors';

export const authGuard: CanActivateFn = (route, state) => {
  const authIsEnabled = inject(Store).select(AppSelectors.authIsEnabled);
  const autoLoginGuard = inject(AutoLoginPartialRoutesGuard);
  return authIsEnabled.pipe(
    take(1),
    mergeMap(authIsEnabled => {
      if(authIsEnabled === false) return of(true);
      return autoLoginGuard.canActivate(route, state);
    }));
};
