import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { filter, identity, take } from 'rxjs';
import { tap } from 'rxjs/operators';
import { AppSelectors } from '../ngrx/app.selectors';

@Component({
  selector: 'app-auth-callback',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex items-center justify-center absolute h-full w-full">
      Please wait...
    </div>
  `,
})
export class AuthCallbackComponent implements OnInit {
  private router = inject(Router);
  private oidcSecurityService = inject(OidcSecurityService);
  private store = inject(Store);


  ngOnInit() {
    this.store.select(AppSelectors.hasFinishedAuthentication).pipe(filter(identity), take(1), tap(() => {
      this.oidcSecurityService.isAuthenticated().pipe(take(1)).subscribe(isAuthenticated => {
        if(isAuthenticated) void this.router.navigate(['/']);
      });
    }));
  }
}
