import { ChangeDetectionStrategy, Component, computed } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { MswEnablementComponent } from './msw-enablement.component';
import { AppSelectors } from './ngrx/app.selectors';
import { NotificationPreferencesComponent } from './notification-preferences.component';

@Component({
  selector: 'app-top-bar',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [MswEnablementComponent, NotificationPreferencesComponent],
  template: `
    <div class="w-full grid grid-cols-3 items-center px-4 bg-slate-600 text-white relative overflow-y-visible">
      <div class="flex items-center">
        @if (isDev()) {
          <app-msw-enablement></app-msw-enablement>
        }
        <span class="ml-2 text-xs text-slate-400">{{ formattedBuildInfo() }}</span>
      </div>
      <button class="text-3xl font-bold mx-4 my-2.5" (click)="navigateToRoot()">Open Pectus</button>
      <div class="flex gap-3 items-center flex-1 justify-end">
        <app-notification-preferences class="mx-3"></app-notification-preferences>
        <p>{{ formatInitials(userData()) ?? 'Anon' }}</p>
        @if (userPicture() === undefined) {
          <div class="codicon codicon-account !text-3xl"></div>
        } @else {
          <img alt="User Picture" [attr.src]="userPicture()" width="32" height="32" class="rounded-full">
        }
      </div>
    </div>
  `,
})
export class TopBarComponent {
  buildInfo = this.store.selectSignal(AppSelectors.buildInfo);
  formattedBuildInfo = computed(() => `#${this.buildInfo()?.build_number}-${this.buildInfo()?.git_sha?.substring(0, 7)}`);
  isDev = computed(() => this.buildInfo()?.build_number?.endsWith('dev'));
  userData = this.store.selectSignal(AppSelectors.userData);
  userPicture = this.store.selectSignal(AppSelectors.userPicture);

  constructor(private store: Store,
              private router: Router) {}

  navigateToRoot() {
    this.router.navigate(['/']).then();
  }

  formatInitials(userData?: { email: string }) {
    return userData?.email?.split('@')?.[0]?.toUpperCase();
  }
}
