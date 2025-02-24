import { ChangeDetectionStrategy, Component } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { UnitControlButtonComponent } from './unit-control-button.component';


@Component({
    selector: 'app-unit-controls',
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [LetDirective, UnitControlButtonComponent],
    template: `
    <div class="flex gap-3.5 flex-wrap" *ngrxLet="controlState as controlState">
      <app-unit-control-button [command]="'Start'" [iconName]="'play'" [toggledColor]="startColor"
                               [toggled]="controlState.is_running"></app-unit-control-button>
      <app-unit-control-button [command]="'Pause'" [iconName]="'debug-pause'"
                               [unCommand]="'Unpause'" [toggledColor]="pauseColor"
                               [toggled]="controlState.is_paused"></app-unit-control-button>
      <app-unit-control-button [command]="'Hold'" [iconName]="'debug-stop'"
                               [unCommand]="'Unhold'" [toggledColor]="pauseColor"
                               [toggled]="controlState.is_holding"></app-unit-control-button>
      <app-unit-control-button [command]="'Stop'" [iconName]="'chrome-close'" [toggledColor]="stopColor"
                               [toggled]="!controlState.is_running"></app-unit-control-button>
    </div>
  `
})
export class UnitControlsComponent {
  readonly startColor = '#047857';
  readonly pauseColor = '#ca8a04';
  readonly stopColor = '#b91c1c';
  protected controlState = this.store.select(DetailsSelectors.controlState);

  constructor(private store: Store) {}
}
