import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-unit-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ng-container *ngrxLet="processUnit as processUnit">
      <div class="flex justify-between items-start gap-4">
        <div class="text-slate-700">
          <h1 class="text-4xl font-bold">{{processUnit?.name}}</h1>
          <span class="text-sm">{{processUnit?.current_user_role}}</span>
        </div>

        <app-unit-controls></app-unit-controls>
      </div>
    </ng-container>
  `,
})
export class UnitHeaderComponent {
  protected processUnit = this.store.select(DetailsSelectors.processUnit);

  constructor(private store: Store) {}
}
