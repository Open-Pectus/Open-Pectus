import { NgIf, TitleCasePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { Error } from '../../api';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { UnitControlsComponent } from './unit-controls.component';

@Component({
  selector: 'app-unit-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    NgIf,
    LetDirective,
    UnitControlsComponent,
    TitleCasePipe,
  ],
  template: `
    <ng-container *ngrxLet="processUnit as processUnit">
      <div class="text-slate-700 mb-4 -mt-2">
        <span class="text-xs mb-2">User role: <b>{{ processUnit?.current_user_role | titlecase }}</b></span>
        <h1 class="text-4xl lg:text-5xl font-bold">{{ processUnit?.name }}</h1>
      </div>
      <app-unit-controls></app-unit-controls>
      <div *ngIf="processUnit?.state?.state === Error.state.ERROR" class="text-rose-800 mt-2 font-bold">
        Interrupted by error! Please see the Error Log below.
      </div>
    </ng-container>
  `,
})
export class UnitHeaderComponent {
  protected Error = Error;
  protected processUnit = this.store.select(DetailsSelectors.processUnit);

  constructor(private store: Store) {}
}
