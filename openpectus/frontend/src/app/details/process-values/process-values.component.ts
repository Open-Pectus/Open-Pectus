import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';

@Component({
  selector: 'app-process-values',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col bg-sky-700 p-1.5 rounded-md shadow-lg">
      <span class="text-2xl font-bold text-gray-100 pb-2 m-2">Process Values</span>
      <div class="flex gap-2 bg-vscode-background-grey rounded-sm p-2 items-start flex-wrap">
        <app-process-value *ngFor="let processValue of (processValues | ngrxPush)" [processValue]="processValue"></app-process-value>
      </div>
    </div>
  `,
})
export class ProcessValuesComponent implements OnInit {
  processValues = this.store.select(DetailsSelectors.processValues);

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.processValuesInitialized());
  }
}
