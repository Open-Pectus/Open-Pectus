import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router } from '@angular/router';
import { LetDirective } from '@ngrx/component';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { MswEnablementComponent } from './msw-enablement.component';

@Component({
  selector: 'app-top-bar',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="w-full flex items-center justify-between px-4 bg-sky-900 text-white relative">
      <app-msw-enablement class="flex-1"></app-msw-enablement>
      <button class="text-3xl font-bold mx-4 my-2.5" (click)="navigateToRoot()">Open Pectus</button>
      <ng-container *ngrxLet="oidcSecurityService.userData$ as userData">
        <div class="flex gap-3 items-center flex-1 justify-end">
          <p>{{getInitials(userData.userData) ?? 'Anon'}}</p>
          <div class="codicon codicon-account !text-3xl"></div>
        </div>
      </ng-container>
    </div>
  `,
  standalone: true,
  imports: [MswEnablementComponent, LetDirective],
})
export class TopBarComponent {
  constructor(private router: Router,
              protected oidcSecurityService: OidcSecurityService) {}

  navigateToRoot() {
    this.router.navigate(['/']).then();
  }

  getInitials(userData: { email: string } | null) {
    return userData?.email?.split('@')?.[0]?.toUpperCase();
  }
}
