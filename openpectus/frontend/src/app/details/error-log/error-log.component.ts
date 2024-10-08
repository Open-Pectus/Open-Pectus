import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input, OnDestroy, OnInit } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { map } from 'rxjs/operators';
import { Defaults } from '../../defaults';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { ErrorLogActions } from './ngrx/error-log.actions';
import { ErrorLogSelectors } from './ngrx/error-log.selectors';

@Component({
  selector: 'app-error-log',
  standalone: true,
  imports: [CommonModule, CollapsibleElementComponent, LetDirective],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Error Log'" [heightResizable]="true" [contentHeight]="200" [codiconName]="'codicon-warning'"
                             (collapseStateChanged)="collapsed = $event" *ngrxLet="errorLog as errorLog">
      @if (!collapsed) {
        <div content class="py-0.5 pr-0.5 h-full grid grid-cols-[auto_1fr] auto-rows-min items-center">
          @for(entry of errorLog.entries; track $index) {
            @if(entry.occurrences !== undefined && entry.occurrences > 1) {
              <div class="h-5 w-5 mx-1.5 text-xs rounded-full text-white flex justify-center items-center select-none"
                   [class.bg-yellow-600]="entry.severity === 'warning'"
                   [class.bg-red-600]="entry.severity === 'error'">
                {{entry.occurrences > 99 ? '99+' : entry.occurrences}}
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
              [<i>{{entry.severity === 'warning' ? 'warn' : entry.severity}}</i>] 
              {{ entry.message }}
            </p>
          }
        </div>
      }
    </app-collapsible-element>
  `,
})
export class ErrorLogComponent implements OnInit, OnDestroy {
  @Input() unitId?: string;
  @Input() recentRunId?: string;
  protected readonly dateFormat = Defaults.dateFormat + '.SSS';
  protected readonly errorLog = this.store.select(ErrorLogSelectors.errorLog).pipe(
    map(errorLog => {
      const sortedEntries = [...errorLog.entries].sort((a, b) => {
        return new Date(b.created_time).valueOf() - new Date(a.created_time).valueOf();
      });
      return {...errorLog, entries: sortedEntries};
    }));
  protected collapsed = false;

  constructor(private store: Store) {}

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

