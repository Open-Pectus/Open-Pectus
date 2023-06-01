import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { ProcessValue } from '../../api';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';

@Component({
  selector: 'app-process-values',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Values'">
      <div class="flex gap-2 p-2 items-start flex-wrap" content>
        <div class="m-auto" *ngIf="(processValues | ngrxPush)?.length === 0">No process values available</div>
        <app-process-value *ngFor="let processValue of (processValues | ngrxPush); trackBy: trackBy"
                           [processValue]="processValue"></app-process-value>
      </div>
    </app-collapsible-element>
  `,
})
export class ProcessValuesComponent implements OnInit, OnDestroy {
  processValues = this.store.select(DetailsSelectors.processValues);

  constructor(private store: Store) {}

  trackBy(index: number, processValue: ProcessValue) {
    return processValue.name;
  }

  ngOnInit() {
    this.store.dispatch(DetailsActions.processValuesInitialized());
  }

  ngOnDestroy() {
    this.store.dispatch(DetailsActions.processValuesDestroyed());
  }
}
