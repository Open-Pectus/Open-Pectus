import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router } from '@angular/router';
import { LetDirective, PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { MswEnablementComponent } from './msw-enablement.component';
import { AppSelectors } from './ngrx/app.selectors';

@Component({
  selector: 'app-top-bar',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [MswEnablementComponent, LetDirective, PushPipe],
  template: `
    <div class="w-full grid grid-cols-[auto_1fr_auto] items-center px-4 bg-slate-600 text-white relative">
      <div class="flex items-center">
        <app-msw-enablement></app-msw-enablement>
        <span class="ml-2 text-xs text-slate-400" *ngrxLet="buildInfo as buildInfo">#{{buildInfo?.build_number}}-{{buildInfo?.git_sha}} </span>
      </div>
      <button class="text-3xl font-bold mx-4 my-2.5" (click)="navigateToRoot()">Open Pectus</button>
      <ng-container *ngrxLet="oidcSecurityService.userData$ as userData">
        <div class="flex gap-3 items-center flex-1 justify-end">
          <p>{{ getInitials(userData.userData) ?? 'Anon' }}</p>
          <div class="codicon codicon-account !text-3xl"></div>
        </div>
      </ng-container>
    </div>
  `,
})
export class TopBarComponent {
  buildInfo = this.store.select(AppSelectors.buildInfo)

  constructor(private store: Store,
              private router: Router,
              protected oidcSecurityService: OidcSecurityService) {}

  navigateToRoot() {
    this.router.navigate(['/']).then();
  }

  getInitials(userData: { email: string } | null) {
    return userData?.email?.split('@')?.[0]?.toUpperCase();
  }
}
