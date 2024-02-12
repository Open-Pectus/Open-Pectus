import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input, OnDestroy, OnInit } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { ErrorLogSeverity } from '../../api';
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
    <app-collapsible-element [name]="'Error Log'" [heightResizable]="true" [contentHeight]="120" [codiconName]="'codicon-warning'"
                             (collapseStateChanged)="collapsed = $event" *ngrxLet="errorLog as errorLog">
      <div content class="p-1 font">
        <p [class.text-yellow-500]="entry.severity === ErrorLogSeverity.WARNING"
           [class.text-red-500]="entry.severity === ErrorLogSeverity.ERROR"
           *ngFor="let entry of errorLog.entries">
          {{ entry.created_time | date:dateFormat }}: [{{ entry.severity }}] {{ entry.message }}
        </p>
      </div>
    </app-collapsible-element>
  `,
})
export class ErrorLogComponent implements OnInit, OnDestroy {
  @Input() unitId?: string;
  @Input() recentRunId?: string;
  protected readonly ErrorLogSeverity = ErrorLogSeverity;
  protected dateFormat = Defaults.dateFormat + '.SSS';
  protected errorLog = this.store.select(ErrorLogSelectors.errorLog);

  protected collapsed = true;

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

