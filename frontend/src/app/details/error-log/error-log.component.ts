import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, input, OnDestroy, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { Defaults } from '../../defaults';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { ErrorLogActions } from './ngrx/error-log.actions';
import { ErrorLogSelectors } from './ngrx/error-log.selectors';

@Component({
  selector: 'app-error-log',
  imports: [CollapsibleElementComponent, DatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Error Log'" [heightResizable]="true" [initialContentHeight]="200" [codiconName]="'codicon-warning'"
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
  readonly unitId = input<string>();
  readonly recentRunId = input<string>();
  protected readonly dateFormat = Defaults.dateFormat + '.SSS';
  protected collapsed = false;
  private store = inject(Store);
  protected readonly errorLog = this.store.selectSignal(ErrorLogSelectors.errorLog);
  protected readonly sortedErrorLog = computed(() => {
    const sortedEntries = [...this.errorLog().entries].sort((a, b) => {
      return new Date(b.created_time).valueOf() - new Date(a.created_time).valueOf();
    });
    return {...this.errorLog(), entries: sortedEntries};
  });

  ngOnInit() {
    const unitId = this.unitId();
    if(unitId !== undefined) this.store.dispatch(ErrorLogActions.errorLogComponentInitializedForUnit({unitId: unitId}));
    const recentRunId = this.recentRunId();
    if(recentRunId !== undefined) {
      this.store.dispatch(ErrorLogActions.errorLogComponentInitializedForRecentRun({recentRunId: recentRunId}));
    }
  }

  ngOnDestroy() {
    this.store.dispatch(ErrorLogActions.errorLogComponentDestroyed());
  }
}

