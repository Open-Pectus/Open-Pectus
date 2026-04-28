import { TitleCasePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Store } from '@ngrx/store';
import { AppSelectors } from '../../ngrx/app.selectors';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ActiveUserComponent } from './active-user.component';
import { UnitControlsComponent } from './unit-controls.component';

@Component({
  selector: 'app-unit-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [UnitControlsComponent, TitleCasePipe, ActiveUserComponent],
  template: `
    <div class="flex justify-between">
      <div>
        <div class="mb-2 text-xs flex gap-4">
          <span>Your role: <b>{{ processUnit()?.current_user_role | titlecase }}</b></span>
          <span>Uod author: <b>{{ processUnit()?.uod_author_name }} <{{ processUnit()?.uod_author_email }}></b></span>
        </div>
        <h1 class="text-4xl lg:text-5xl font-bold text-slate-700 mb-4">{{ processUnit()?.name }}</h1>
        <app-unit-controls />
        <div class="text-rose-800 mt-2 font-bold">
          @if (processUnit()?.state?.state === 'error') {
            Interrupted by error! Please see the Error Log below.
          }
          @if (webSocketIsDisconnected()) {
            Websocket is disconnected! You will not see updates in run information.
          }
        </div>
      </div>

      @if (otherActiveUsers().length !== 0) {
        <div class="flex flex-col items-end gap-1">
          <span class="text-xs">Other active users:</span>
          <div class="grid grid-rows-5 items-end gap-y-1.5 gap-x-3 grid-flow-col" dir="rtl">
            @for (activeUser of otherActiveUsers(); track activeUser.id) {
              <app-active-user [activeUser]="activeUser" dir="ltr" />
            }
          </div>
        </div>
      }
    </div>
  `,
})
export class UnitHeaderComponent {
  private store = inject(Store);

  protected processUnit = this.store.selectSignal(DetailsSelectors.processUnit);
  protected webSocketIsDisconnected = this.store.selectSignal(AppSelectors.webSocketIsDisconnected);
  protected otherActiveUsers = this.store.selectSignal(DetailsSelectors.otherActiveUsers);
}
