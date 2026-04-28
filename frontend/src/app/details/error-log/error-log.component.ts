import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, Input, OnDestroy, OnInit, inject } from '@angular/core';
import { Store } from '@ngrx/store';
import { Defaults } from '../../defaults';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { ErrorLogActions } from './ngrx/error-log.actions';
import { ErrorLogSelectors } from './ngrx/error-log.selectors';

@Component({
  selector: 'app-error-log',
  imports: [CommonModule, CollapsibleElementComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Error Log'" [heightResizable]="true" [contentHeight]="200" [codiconName]="'codicon-warning'"
                             (collapseStateChanged)="collapsed = $event">
      @if (!collapsed) {
        <div content class="py-0.5 pr-0.5 h-full grid grid-cols-[auto_1fr] auto-rows-min items-center">
          @for (entry of sortedErrorLog().entries; track $index) {
            @if (entry.occurrences !== undefined && entry.occurrences > 1) {
              <div class="h-5 w-5 mx-1.5 text-xs rounded-full text-white flex justify-center items-center select-none"
                   [class.bg-yellow-600]="entry.severity === 'warning'"
                   [class.bg-red-600]="entry.severity === 'error'">
                {{ entry.occurrences > 99 ? '99+' : entry.occurrences }}
              </div>
            } @else {
              <span></span>
            }
            <p class="pl-0.5"
               [class.text-yellow-800]="entry.severity === 'warning'"
               [class.text-red-800]="entry.severity === 'error'"
               [class.bg-yellow-100]="entry.severity === 'warning'"
               [class.bg-red-100]="entry.severity === 'error'">
              {{ entry.created_time | date:dateFormat }}
              [<i>{{ entry.severity === 'warning' ? 'warn' : entry.severity }}</i>]
              {{ entry.message }}
            </p>
          }
        </div>
      }
    </app-collapsible-element>
  `
})
export class ErrorLogComponent implements OnInit, OnDestroy {
  private store = inject(Store);

  @Input() unitId?: string;
  @Input() recentRunId?: string;
  protected readonly dateFormat = Defaults.dateFormat + '.SSS';
  protected readonly errorLog = this.store.selectSignal(ErrorLogSelectors.errorLog);
  protected readonly sortedErrorLog = computed(() => {
    const sortedEntries = [...this.errorLog().entries].sort((a, b) => {
      return new Date(b.created_time).valueOf() - new Date(a.created_time).valueOf();
    });
    return {...this.errorLog(), entries: sortedEntries};
  });
  protected collapsed = false;

  ngOnInit() {
    if(this.unitId !== undefined) this.store.dispatch(ErrorLogActions.errorLogComponentInitializedForUnit({unitId: this.unitId}));
    if(this.recentRunId !== undefined) {
      this.store.dispatch(ErrorLogActions.errorLogComponentInitializedForRecentRun({recentRunId: this.recentRunId}));
    }
  }

  ngOnDestroy() {
    this.store.dispatch(ErrorLogActions.errorLogComponentDestroyed());
  }
}

