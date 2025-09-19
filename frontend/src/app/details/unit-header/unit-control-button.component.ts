import { NgClass, TitleCasePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, input, Input, signal } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsActions } from '../ngrx/details.actions';
import { UnitControlCommands } from '../unit-control-commands.';

@Component({
  selector: 'app-unit-control-button',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgClass, TitleCasePipe],
  host: {style: 'position: relative'},
  template: `
    <button class="py-2 pr-5 pl-3.5 rounded-lg text-white bg-sky-700 flex items-center gap-2 tracking-wider"
            (click)="executeCommand()"
            [disabled]="disabled || (toggled() && unCommand === undefined)"
            [class.bg-slate-400]="disabled"
            [style.margin]="showPressed() ? '3px 0 0 2px' : '0 2px 3px 0'"
            [style.background-color]="toggled() ? toggledColor : null"
            [style.box-shadow]="showPressed() ? null : disabled ? '2.5px 3px #cbd5e1' : ('2.5px 3px color-mix(in srgb, '+shadowColor()+', black 10%)')">
      <span class="codicon" [ngClass]="'codicon-'+iconName"></span>{{ command | titlecase }}
    </button>
    @if (showLock()) {
      <button class="absolute top-0 w-full h-full flex items-center" (click)="onLockClicked()">
        <div class="absolute ml-2.5 mb-[3px] rounded-full w-6 h-6 bg-gray-700 flex items-center justify-center border border-gray-300">
          <div class="codicon codicon-lock !font-bolder text-white"></div>
        </div>
      </button>
    }
  `
})
export class UnitControlButtonComponent {
  @Input() command?: UnitControlCommands;
  @Input() unCommand?: UnitControlCommands;
  @Input() iconName?: string;
  @Input() disabled = false;
  toggled = input(false);
  optimisticClicked = input(false);
  @Input() toggledColor = '#0f172a';
  hasLock = input(false);
  isLocked = signal(true);
  showLock = computed(() => this.hasLock() && this.isLocked() && !this.toggled() && !this.optimisticClicked());
  showPressed = computed(() => (this.toggled() && !this.optimisticClicked()) || (!this.toggled() && this.optimisticClicked()));
  shadowColor = computed(() => this.toggled() ? this.toggledColor : '#0369a1');

  constructor(private store: Store) {}

  executeCommand() {
    if(this.optimisticClicked()) return;
    const command = this.toggled() ? this.unCommand : this.command;
    if(command === undefined) return;
    this.store.dispatch(DetailsActions.processUnitCommandButtonClicked({command}));
    this.isLocked.set(true);
  }

  onLockClicked() {
    this.isLocked.set(false);
    setTimeout(() => {
      if(!this.toggled()) this.isLocked.set(true);
    }, 4000);
  }
}
