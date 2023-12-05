import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { RunLogActions } from './ngrx/run-log.actions';

@Component({
  selector: 'app-run-log-filters',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [NgIf],
  template: `
    <div class="flex gap-3 items-center flex-wrap justify-end">
      <label class="relative">
        <input type="text" placeholder="Filter Run Log" size="20"
               class="border border-slate-200 placeholder:text-slate-400 text-white bg-transparent outline-none rounded p-1 h-8"
               #filterInput (input)="filterTextChanged(filterInput.value)">
        <button *ngIf="filterInput.value.length !== 0" class="p-2 codicon codicon-chrome-close absolute right-0"
                (click)="filterInput.value = ''; filterTextChanged('')"></button>
      </label>
      <label class="flex items-center gap-1 cursor-pointer border rounded px-1 border-slate-200 h-8" *ngIf="showRunningFilter">
        In progress only
        <input type="checkbox" (input)="onlyRunningChanged(onlyRunningCheckbox.checked)" #onlyRunningCheckbox
               [class.codicon-pass]="onlyRunningCheckbox.checked" [class.codicon-circle-large]="!onlyRunningCheckbox.checked"
               class="w-5 !text-xl appearance-none font-bold opacity-25 text-white checked:opacity-100 codicon cursor-pointer">
      </label>
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
