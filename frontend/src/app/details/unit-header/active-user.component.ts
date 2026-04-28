import { HttpClient } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, input, inject } from '@angular/core';
import { toObservable } from '@angular/core/rxjs-interop';
import { Store } from '@ngrx/store';
import { combineLatest, EMPTY, map, shareReplay, switchMap } from 'rxjs';
import { ActiveUser } from '../../api';
import { AppSelectors } from '../../ngrx/app.selectors';
import { AsyncPipe } from '@angular/common';

@Component({
  selector: 'app-active-user',
  imports: [AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex gap-1 items-center justify-end h-6">
      <span class="text-sm">{{ activeUser().name }}</span>
      @if ((profileImage | async) === undefined) {
        <div class="codicon codicon-account !text-2xl"></div>
      } @else {
        <img [attr.src]="profileImage | async" alt="PI" width="24" height="24" class="rounded-full">
      }
    </div>
  `,
})
export class ActiveUserComponent {
  private store = inject(Store);
  private httpClient = inject(HttpClient);

  activeUser = input.required<ActiveUser>();
  authIsEnabled = this.store.select(AppSelectors.authIsEnabled);
  profileImage = combineLatest([toObservable(this.activeUser), this.authIsEnabled]).pipe(
    switchMap(([activeUser, authIsEnabled]) => {
      if(!authIsEnabled) return EMPTY;
      return this.httpClient.get(
        `https://graph.microsoft.com/beta/users/${activeUser.id}/photos/48x48/$value`,
        {headers: {accept: 'image/jpeg'}, responseType: 'blob'},
      );
    }),
    map(imageBlob => URL.createObjectURL(imageBlob)),
    shareReplay(1),
  );
}
