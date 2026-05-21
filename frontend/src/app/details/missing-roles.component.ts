import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Store } from '@ngrx/store';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-missing-roles',
  template: `
    @if (missingRoles() !== undefined) {
      <span class="absolute-center lg:text-xl font-bold whitespace-nowrap flex flex-col gap-4 items-center">
      <p>You are missing one of these roles:</p>
      <p>{{ missingRoles() }}</p>
      <button class="bg-slate-600 rounded text-white px-4 py-2" (click)="refreshToken()">Force refresh session and try again</button>
    </span>
    } @else {
      <ng-content />
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class MissingRolesComponent {
  private store = inject(Store);
  private oidcService = inject(OidcSecurityService);

  protected readonly missingRoles = this.store.selectSignal(DetailsSelectors.missingRoles);

  protected refreshToken() {
    this.oidcService.forceRefreshSession().subscribe(() => window.location.reload());
  }
}
