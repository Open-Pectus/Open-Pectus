import { HttpClient } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { toObservable } from '@angular/core/rxjs-interop';
import { PushPipe } from '@ngrx/component';
import { map, shareReplay, switchMap } from 'rxjs';
import { ActiveUser } from '../../api';

@Component({
  selector: 'app-active-user',
  imports: [PushPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex gap-1 items-center h-6">
      <span class="text-sm">{{ activeUser().name }}</span>
      @if ((profileImage | ngrxPush) === undefined) {
        <div class="codicon codicon-account !text-2xl"></div>
      } @else {
        <img [attr.src]="(profileImage | ngrxPush)" alt="PI" width="24" height="24" class="rounded-full">
      }
    </div>
  `,
})
export class ActiveUserComponent {
  activeUser = input.required<ActiveUser>();
  profileImage = toObservable(this.activeUser).pipe(
    switchMap(activeUser => this.httpClient.get(
      `https://graph.microsoft.com/beta/users/${activeUser.id}/photos/48x48/$value`,
      {headers: {accept: 'image/jpeg'}, responseType: 'blob'},
    )),
    map(imageBlob => URL.createObjectURL(imageBlob)),
    shareReplay(1),
  );

  constructor(private httpClient: HttpClient) {}
}
