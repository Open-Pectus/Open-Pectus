import { TitleCasePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { LetDirective, PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { map } from 'rxjs';
import { ActiveUser } from '../../api';
import { AppSelectors } from '../../ngrx/app.selectors';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ActiveUserComponent } from './active-user.component';
import { UnitControlsComponent } from './unit-controls.component';

@Component({
  selector: 'app-unit-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [LetDirective, UnitControlsComponent, TitleCasePipe, PushPipe, ActiveUserComponent],
  template: `
    <div class="flex justify-between" *ngrxLet="processUnit as processUnit">
      <div>
        <div class="mb-2 text-xs flex gap-4">
          <span>Your role: <b>{{ processUnit?.current_user_role | titlecase }}</b></span>
          <span>Uod author: <b>{{ processUnit?.uod_author_name }} <{{ processUnit?.uod_author_email }}></b></span>
        </div>
        <h1 class="text-4xl lg:text-5xl font-bold text-slate-700 mb-4">{{ processUnit?.name }}</h1>
        <app-unit-controls></app-unit-controls>
        <div class="text-rose-800 mt-2 font-bold">
          @if (processUnit?.state?.state === 'error') {
            Interrupted by error! Please see the Error Log below.
          }
          @if (webSocketIsDisconnected | ngrxPush) {
            Websocket is disconnected! You will not see updates in run information.
          }
        </div>
      </div>

      <div class="flex flex-col items-end gap-1">
        <span class="text-xs">Other active users:</span>
        <div class="grid grid-rows-5 items-end gap-y-1.5 gap-x-3 grid-flow-col" dir="rtl">
          @for (activeUser of (activeUsers | ngrxPush); track $index) {
            <app-active-user [activeUser]="activeUser" dir="ltr"></app-active-user>
          }
        </div>
      </div>
    </div>
  `,
})
export class UnitHeaderComponent {
  protected processUnit = this.store.select(DetailsSelectors.processUnit);
  protected webSocketIsDisconnected = this.store.select(AppSelectors.webSocketIsDisconnected);
  protected activeUsers = this.store.select(DetailsSelectors.activeUsers).pipe<ActiveUser[]>(map(activeUsers => {
    if(activeUsers.length === 0) return [];
    return Array(3).fill(activeUsers[0]);
  }));

  constructor(private store: Store) {}
}
