import { ChangeDetectionStrategy, Component } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
    selector: 'app-missing-roles',
    imports: [
        PushPipe,
    ],
    template: `
    @if ((missingRoles | ngrxPush) !== undefined) {
      <span class="absolute-center lg:text-xl font-bold whitespace-nowrap flex flex-col gap-4 items-center">
      <p>You are missing one of these roles:</p>
      <p>{{ missingRoles | ngrxPush }}</p>
      <button class="bg-slate-600 rounded text-white px-4 py-2" (click)="refreshToken()">Force refresh session and try again</button>
    </span>
    } @else {
      <ng-content></ng-content>
    }
  `,
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class MissingRolesComponent {
  protected readonly missingRoles = this.store.select(DetailsSelectors.missingRoles);

  constructor(private store: Store,
              private oidcService: OidcSecurityService) {}

  protected refreshToken() {
    this.oidcService.forceRefreshSession().subscribe(() => window.location.reload());
  }
}
