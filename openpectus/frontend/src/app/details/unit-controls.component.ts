import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { SystemState } from 'src/msw/handlers';
import { DetailsSelectors } from './ngrx/details.selectors';


@Component({
  selector: 'app-unit-controls',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex gap-3" *ngrxLet="systemState as systemState">
      <app-unit-control-button [command]="'Start'" [iconName]="'play'" [toggledColor]="startColor"
                               [toggled]="systemState !== SystemState.Stopped"></app-unit-control-button>
      <app-unit-control-button [command]="'Pause'" [iconName]="'debug-pause'"
                               [unCommand]="'Unpause'" [toggledColor]="pauseColor"
                               [disabled]="systemState === SystemState.Stopped"
                               [toggled]="systemState === SystemState.Paused || systemState === SystemState.PausedAndHolding"></app-unit-control-button>
      <app-unit-control-button [command]="'Hold'" [iconName]="'debug-stop'"
                               [unCommand]="'Unhold'" [toggledColor]="pauseColor"
                               [disabled]="systemState === SystemState.Stopped"
                               [toggled]="systemState === SystemState.Holding || systemState === SystemState.PausedAndHolding"></app-unit-control-button>
      <app-unit-control-button [command]="'Stop'" [iconName]="'chrome-close'" [toggledColor]="stopColor"
                               [toggled]="systemState === SystemState.Stopped"></app-unit-control-button>
    </div>
  `,
})
export class UnitControlsComponent {
  readonly startColor = '#047857';
  readonly pauseColor = '#ca8a04';
  readonly stopColor = '#b91c1c';
  protected readonly SystemState = SystemState;
  protected systemState = this.store.select(DetailsSelectors.systemState);

  constructor(private store: Store) {}
}
