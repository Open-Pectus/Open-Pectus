import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router } from '@angular/router';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { FrontendPubsubService } from './api';

@Component({
  selector: 'app-top-bar',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="w-full flex items-center justify-between px-4 bg-sky-900 text-white relative">
      <div class="flex flex-1">
        <app-msw-enablement></app-msw-enablement>
        <button (click)="frontendPubsubService.triggerPubsub().subscribe()">trigger pubsub</button>
      </div>
      <button class="text-3xl font-bold mx-4 my-2.5" (click)="navigateToRoot()">Open Pectus</button>
      <ng-container *ngrxLet="oidcSecurityService.userData$ as userData">
        <div class="flex gap-3 items-center flex-1 justify-end">
          <p>{{getInitials(userData.userData) ?? 'Anon'}}</p>
          <div class="codicon codicon-account !text-3xl"></div>
        </div>
      </ng-container>
    </div>
  `,
})
export class TopBarComponent {
  constructor(private router: Router,
              protected oidcSecurityService: OidcSecurityService,
              protected frontendPubsubService: FrontendPubsubService) {}

  navigateToRoot() {
    this.router.navigate(['/']).then();
  }

  getInitials(userData: { email: string } | null) {
    return userData?.email?.split('@')?.[0]?.toUpperCase();
  }
}
