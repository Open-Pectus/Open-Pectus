import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router } from '@angular/router';
import { LetDirective, PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { MswEnablementComponent } from './msw-enablement.component';
import { AppSelectors } from './ngrx/app.selectors';

@Component({
    selector: 'app-top-bar',
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [MswEnablementComponent, LetDirective, PushPipe],
    template: `
    <div class="w-full grid grid-cols-3 items-center px-4 bg-slate-600 text-white relative">
      <div class="flex items-center">
        <app-msw-enablement></app-msw-enablement>
        <span class="ml-2 text-xs text-slate-400" *ngrxLet="buildInfo as buildInfo">
          #{{ buildInfo?.build_number }}-{{ buildInfo?.git_sha?.substring(0, 7) }}
        </span>
      </div>
      <button class="text-3xl font-bold mx-4 my-2.5" (click)="navigateToRoot()">Open Pectus</button>
      <div class="flex gap-3 items-center flex-1 justify-end">
        <p>{{ formatInitials(userData | ngrxPush) ?? 'Anon' }}</p>
        @if ((userPicture | ngrxPush) === undefined) {
          <div class="codicon codicon-account !text-3xl"></div>
        } @else {
          <img alt="User Picture" [attr.src]="userPicture | ngrxPush" width="32" height="32" class="rounded-full">
        }
      </div>
    </div>
  `
})
export class TopBarComponent {
  buildInfo = this.store.select(AppSelectors.buildInfo);
  userData = this.store.select(AppSelectors.userData);
  userPicture = this.store.select(AppSelectors.userPicture);

  constructor(private store: Store,
              private router: Router) {}

  navigateToRoot() {
    this.router.navigate(['/']).then();
  }

  formatInitials(userData?: { email: string }) {
    return userData?.email?.split('@')?.[0]?.toUpperCase();
  }
}
