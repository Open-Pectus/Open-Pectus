import { ChangeDetectionStrategy, Component, inject, input } from '@angular/core';
import { Store } from '@ngrx/store';
import { RunLogActions } from '../ngrx/run-log.actions';
import { RunLogLineButtonComponent } from './run-log-line-button.component';

@Component({
    selector: 'app-run-log-line-cancel-button',
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [RunLogLineButtonComponent],
    template: `
    <app-run-log-line-button buttonText="Cancel"
                             colorClass="bg-red-200"
                             confirmColorClass="bg-red-800"
                             codiconClass="codicon-chrome-close"
                             (confirmedClick)="onClick()" />
  `
})
export class RunLogLineCancelButtonComponent {
  private store = inject(Store);

  readonly lineId = input<string>();

  onClick() {
    const lineId = this.lineId();
    if(lineId === undefined) return;
    this.store.dispatch(RunLogActions.cancelLineButtonClicked({lineId: lineId}));
  }
}
