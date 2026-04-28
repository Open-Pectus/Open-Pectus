import { ChangeDetectionStrategy, Component, inject, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { ToggleButtonComponent } from '../../shared/toggle-button.component';
import { RunLogActions } from './ngrx/run-log.actions';

@Component({
  selector: 'app-run-log-filters',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ToggleButtonComponent],
  template: `
    <div class="flex gap-3 items-center flex-wrap justify-end">
      <label class="relative">
        <input type="text" placeholder="Filter Run Log" size="20"
               class="bg-white border border-gray-300 placeholder:text-gray-400 bg-transparent outline-none rounded p-1 h-8"
               #filterInput (input)="filterTextChanged(filterInput.value)">
        @if (filterInput.value.length !== 0) {
          <button class="p-2 codicon codicon-chrome-close absolute right-0"
                  (click)="filterInput.value = ''; filterTextChanged('')"></button>
        }
      </label>
      <app-toggle-button [label]="'In progress only'" (changed)="onlyRunningChanged($event)"></app-toggle-button>
    </div>
  `
})
export class RunLogFiltersComponent {
  @Input() showRunningFilter = true;
  private store = inject(Store);

  filterTextChanged(filterText: string) {
    this.store.dispatch(RunLogActions.filterTextChanged({filterText}));
  }

  onlyRunningChanged(onlyRunning: boolean) {
    this.store.dispatch(RunLogActions.onlyRunningFilterChanged({onlyRunning}));
  }
}
