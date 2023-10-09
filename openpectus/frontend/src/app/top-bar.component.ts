import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router } from '@angular/router';
import { OidcSecurityService } from 'angular-auth-oidc-client';

@Component({
  selector: 'app-top-bar',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="w-full h-24 md:h-14 flex items-center justify-between px-4 bg-sky-900 text-white relative">
      <app-msw-enablement class="flex-1"></app-msw-enablement>
      <button class="text-3xl font-bold mx-4" (click)="navigateToRoot()">Open Pectus</button>
      <ng-container *ngrxLet="oidcSecurityService.userData$ as userData">
        <div class="flex gap-4 items-center flex-1 justify-end">
          <p>{{userData.userData?.name ?? 'Anonymous'}}</p>
          <div class="codicon codicon-account !text-3xl"></div>
        </div>
      </ng-container>
    </div>
  `,
})
export class TopBarComponent {
  constructor(private router: Router,
              protected oidcSecurityService: OidcSecurityService) {}

  navigateToRoot() {
    this.router.navigate(['/']).then();
  }
}
