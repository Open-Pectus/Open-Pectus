import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { ToggleButtonComponent } from '../../shared/toggle-button.component';
import { RunLogActions } from './ngrx/run-log.actions';

@Component({
  selector: 'app-run-log-filters',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [NgIf, ToggleButtonComponent],
  template: `
    <div class="flex gap-3 items-center flex-wrap justify-end">
      <label class="relative">
        <input type="text" placeholder="Filter Run Log" size="20"
               class="border border-slate-200 placeholder:text-slate-400 text-white bg-transparent outline-none rounded p-1 h-8"
               #filterInput (input)="filterTextChanged(filterInput.value)">
        <button *ngIf="filterInput.value.length !== 0" class="p-2 codicon codicon-chrome-close absolute right-0"
                (click)="filterInput.value = ''; filterTextChanged('')"></button>
      </label>
      <app-toggle-button [label]="'In progress only'" (changed)="onlyRunningChanged($event)"></app-toggle-button>
    </div>
  `,
})
export class RunLogFiltersComponent {
  @Input() showRunningFilter = true;

  constructor(private store: Store) {}

  filterTextChanged(filterText: string) {
    this.store.dispatch(RunLogActions.filterTextChanged({filterText}));
  }

  onlyRunningChanged(onlyRunning: boolean) {
    this.store.dispatch(RunLogActions.onlyRunningFilterChanged({onlyRunning}));
  }
}
