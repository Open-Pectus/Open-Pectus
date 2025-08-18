import { NgClass, TitleCasePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsActions } from '../ngrx/details.actions';

@Component({
    selector: 'app-unit-control-button',
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [NgClass, TitleCasePipe],
    template: `
    <button class="py-2 pr-5 pl-3.5 rounded-lg text-white bg-sky-700 flex items-center gap-2 tracking-wider"
            (click)="executeCommand()"
            [disabled]="disabled || (toggled && unCommand === undefined)"
            [class.bg-slate-400]="disabled"
            [style.margin]="toggled ? '3px 0 0 2px' : '0 2px 3px 0'"
            [style.background-color]="toggled ? toggledColor : null"
            [style.box-shadow]="toggled ? null : disabled ? '2.5px 3px #cbd5e1' : '2.5px 3px #075985'">
      <span class="codicon" [ngClass]="'codicon-'+iconName"></span>{{ command | titlecase }}
    </button>
  `
})
export class UnitControlButtonComponent {
  @Input() command?: string;
  @Input() unCommand?: string;
  @Input() iconName?: string;
  @Input() disabled = false;
  @Input() toggled = false;
  @Input() toggledColor = '#0f172a';

  constructor(private store: Store) {}

  executeCommand() {
    const command = this.toggled ? this.unCommand : this.command;
    if(command === undefined) return;
    this.store.dispatch(DetailsActions.processUnitCommandButtonClicked({command}));
  }
}
