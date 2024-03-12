import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { RunLogActions } from '../ngrx/run-log.actions';
import { RunLogLineButtonComponent } from './run-log-line-button.component';

@Component({
  selector: 'app-run-log-line-cancel-button',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [RunLogLineButtonComponent],
  template: `
    <app-run-log-line-button buttonText="Cancel"
                             colorClass="bg-red-200"
                             confirmColorClass="bg-red-800"
                             codiconClass="codicon-chrome-close"
                             (confirmedClick)="onClick()">
    </app-run-log-line-button>
  `,
})
export class RunLogLineCancelButtonComponent {
  @Input() lineId?: string;

  constructor(private store: Store) {}

  onClick() {
    if(this.lineId === undefined) return;
    this.store.dispatch(RunLogActions.cancelLineButtonClicked({lineId: this.lineId}));
  }
}
