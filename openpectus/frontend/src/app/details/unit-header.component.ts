import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-unit-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ng-container *ngrxLet="processUnit as processUnit">
      <div class="text-slate-700 mb-4 -mt-2">
        <span class="text-xs mb-2">User role: <b>{{processUnit?.current_user_role | titlecase}}</b></span>
        <h1 class="text-4xl lg:text-5xl font-bold">{{processUnit?.name}}</h1>
      </div>
      <app-unit-controls></app-unit-controls>
    </ng-container>
  `,
})
export class UnitHeaderComponent {
  protected processUnit = this.store.select(DetailsSelectors.processUnit);

  constructor(private store: Store) {}
}
