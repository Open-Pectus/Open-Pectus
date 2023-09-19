import { inject } from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { Store } from '@ngrx/store';
import { AutoLoginPartialRoutesGuard } from 'angular-auth-oidc-client';
import { mergeMap, of } from 'rxjs';
import { AppSelectors } from '../ngrx/app.selectors';

export const authGuard: CanActivateFn = (route, state) => {
  const authIsEnabled = inject(Store).select(AppSelectors.authIsEnabled);
  const autoLoginGuard = inject(AutoLoginPartialRoutesGuard);
  return authIsEnabled.pipe(
    mergeMap(authIsEnabled => {
      if(authIsEnabled) return autoLoginGuard.canActivate(route, state);
      return of(true);
    }));
};
