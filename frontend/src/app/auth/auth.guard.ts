import { inject } from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { Store } from '@ngrx/store';
import { AutoLoginPartialRoutesGuard } from 'angular-auth-oidc-client';
import { filter, mergeMap, of, take } from 'rxjs';
import { AppSelectors } from '../ngrx/app.selectors';
import { UtilMethods } from '../shared/util-methods';

export const authGuard: CanActivateFn = (route, state) => {
  const authIsEnabled = inject(Store).select(AppSelectors.authIsEnabled);
  const autoLoginGuard = inject(AutoLoginPartialRoutesGuard);
  return authIsEnabled.pipe(
    filter(UtilMethods.isNotNullOrUndefined),
    take(1),
    mergeMap(authIsEnabled => {
      if(!authIsEnabled) return of(true);
      return autoLoginGuard.canActivate(route, state);
    }));
};
