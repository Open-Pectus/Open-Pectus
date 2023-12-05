import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { RunLogActions } from '../ngrx/run-log.actions';
import { RunLogLineButtonComponent } from './run-log-line-button.component';

@Component({
  selector: 'app-run-log-line-force-button',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [RunLogLineButtonComponent],
  template: `
    <app-run-log-line-button buttonText="Force"
                             colorClass="bg-yellow-100"
                             confirmColorClass="bg-yellow-600"
                             codiconClass="codicon-play"
                             (confirmedClick)="onClick()">
    </app-run-log-line-button>
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
