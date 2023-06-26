import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsActions } from './ngrx/details.actions';

@Component({
  selector: 'app-unit-details',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex justify-center">
      <div class="grid grid-cols-1 2xl:grid-cols-2 w-full p-8 gap-8">
        <app-unit-header></app-unit-header>
        <app-process-values></app-process-values>
        <app-method-editor></app-method-editor>
        <app-commands></app-commands>
        <app-run-log></app-run-log>
        <app-process-plot></app-process-plot>
        <app-process-diagram></app-process-diagram>
      </div>
    </div>
  `,
})
export class UnitDetailsComponent implements OnInit, OnDestroy {
  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.unitDetailsInitialized());
  }

  ngOnDestroy() {
    this.store.dispatch(DetailsActions.unitDetailsDestroyed());
  }
}
