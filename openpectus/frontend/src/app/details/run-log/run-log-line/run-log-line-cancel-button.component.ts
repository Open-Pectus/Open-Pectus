import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { RunLogActions } from '../ngrx/run-log.actions';

@Component({
  selector: 'app-run-log-line-cancel-button',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-run-log-line-button buttonText="Cancel" colorClass="bg-red-800" codiconClass="codicon-chrome-close"
                             (confirmedClick)="onClick()"></app-run-log-line-button>
  `,
})
export class RunLogLineCancelButtonComponent {
  @Input() lineId?: number;

  constructor(private store: Store) {}

  onClick() {
    if(this.lineId === undefined) return;
    this.store.dispatch(RunLogActions.cancelLineButtonClicked({lineId: this.lineId}));
  }
}
