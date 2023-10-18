import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { RunLogActions } from '../ngrx/run-log.actions';

@Component({
  selector: 'app-run-log-line-force-button',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-run-log-line-button buttonText="Force" colorClass="bg-green-800" codiconClass="codicon-play"
                             (confirmedClick)="onClick()"></app-run-log-line-button>
  `,
})
export class RunLogLineForceButtonComponent {
  @Input() lineId?: number;

  constructor(private store: Store) {}

  onClick() {
    if(this.lineId === undefined) return;
    this.store.dispatch(RunLogActions.forceLineButtonClicked({lineId: this.lineId}));
  }
}
