import { ChangeDetectionStrategy, Component } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { UnitControlButtonComponent } from './unit-control-button.component';
import { UnitControlCommands } from '../unit-control-commands.';


@Component({
  selector: 'app-unit-controls',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [LetDirective, UnitControlButtonComponent],
  template: `
    <div class="flex gap-3.5 flex-wrap" *ngrxLet="controlState as controlState">
      <app-unit-control-button [command]="UnitControlCommands.Start" [iconName]="'play'" [toggledColor]="startColor"
                               [toggled]="controlState.is_running"></app-unit-control-button>
      <app-unit-control-button [command]="UnitControlCommands.Pause" [iconName]="'debug-pause'"
                               [unCommand]="UnitControlCommands.Unpause" [toggledColor]="pauseColor"
                               [toggled]="controlState.is_paused"></app-unit-control-button>
      <app-unit-control-button [command]="UnitControlCommands.Hold" [iconName]="'debug-stop'"
                               [unCommand]="UnitControlCommands.Unhold" [toggledColor]="pauseColor"
                               [toggled]="controlState.is_holding"></app-unit-control-button>
      <app-unit-control-button [command]="UnitControlCommands.Stop" [iconName]="'chrome-close'" [toggledColor]="stopColor"
                               [toggled]="!controlState.is_running" [hasLock]="true"></app-unit-control-button>
    </div>
  `
})
export class UnitControlsComponent {
  readonly startColor = '#047857';
  readonly pauseColor = '#ca8a04';
  readonly stopColor = '#b91c1c';
  protected readonly UnitControlCommands = UnitControlCommands;
  protected controlState = this.store.select(DetailsSelectors.controlState);

  constructor(private store: Store) {}
}
