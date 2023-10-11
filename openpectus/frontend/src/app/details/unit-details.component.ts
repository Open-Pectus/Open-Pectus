import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { selectRouteParam } from '../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from './details-routing-url-parts';
import { DetailsActions } from './ngrx/details.actions';

@Component({
  selector: 'app-unit-details',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex justify-center">
      <div class="grid grid-cols-1 2xl:grid-cols-2 w-full lg:px-6 lg:py-8 gap-4 lg:gap-8" *ngrxLet="unitId as unitId">
        <app-unit-header class="mx-2 my-3 lg:m-0"></app-unit-header>
        <app-process-values></app-process-values>
        <app-method-editor [unitId]="unitId"></app-method-editor>
        <app-commands></app-commands>
        <app-run-log [unitId]="unitId"></app-run-log>
        <app-process-diagram></app-process-diagram>
        <app-process-plot-container class="2xl:col-span-2" [unitId]="unitId"></app-process-plot-container>
      </div>
    </div>
  `,
})
export class UnitDetailsComponent implements OnInit, OnDestroy {
  protected unitId = this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName));

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.unitDetailsInitialized());
  }

  ngOnDestroy() {
    this.store.dispatch(DetailsActions.unitDetailsDestroyed());
  }
}
