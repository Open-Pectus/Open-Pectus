import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input, OnDestroy, OnInit } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { map } from 'rxjs/operators';
import { ErrorLogSeverity } from '../../api/models/ErrorLogSeverity';
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
        <div content class="p-1 h-full">
          <p [class.text-yellow-500]="entry.severity === ErrorLogSeverity.WARNING"
             [class.text-red-500]="entry.severity === ErrorLogSeverity.ERROR"
             *ngFor="let entry of errorLog.entries">
            {{ entry.created_time | date:dateFormat }}: [{{ entry.severity }}] {{ entry.message }}
          </p>
        </div>
      }
    </app-collapsible-element>
  `,
})
export class ErrorLogComponent implements OnInit, OnDestroy {
  @Input() unitId?: string;
  @Input() recentRunId?: string;
  protected readonly ErrorLogSeverity = ErrorLogSeverity;
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

