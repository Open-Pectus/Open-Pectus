import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { CommandSource } from '../api';
import { DetailsActions } from './ngrx/details.actions';

@Component({
  selector: 'app-unit-control-button',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button class="py-2 px-3.5 rounded-lg text-white bg-slate-700 flex items-center gap-2"
            (click)="executeCommand()" [disabled]="disabled" [class.!bg-gray-300]="disabled">
      <span class="codicon" [ngClass]="'codicon-'+iconName"></span>{{command | titlecase}}
    </button>
  `,
})
export class UnitControlButtonComponent {
  @Input() command?: string;
  @Input() iconName?: string;
  @Input() disabled = false;

  constructor(private store: Store) {}

  executeCommand() {
    if(this.command === undefined || this.disabled) return;
    this.store.dispatch(DetailsActions.processUnitCommandButtonClicked({command: {command: this.command, source: CommandSource.UNIT_BUTTON}}));
  }
}
