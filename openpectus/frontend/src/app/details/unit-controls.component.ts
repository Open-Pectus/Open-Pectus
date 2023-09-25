import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { SystemState } from 'src/msw/handlers';
import { DetailsSelectors } from './ngrx/details.selectors';


@Component({
  selector: 'app-unit-controls',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex gap-2.5" *ngrxLet="systemState as systemState">
      <app-unit-control-button [command]="'start'" [iconName]="'play'"
                               [disabled]="systemState === SystemState.Running"></app-unit-control-button>
      <app-unit-control-button [command]="'pause'" [iconName]="'debug-pause'"
                               [disabled]="systemState === SystemState.Paused || systemState === SystemState.Holding"></app-unit-control-button>
      <app-unit-control-button [command]="'hold'" [iconName]="'debug-stop'"
                               [disabled]="systemState === SystemState.Holding"></app-unit-control-button>
      <app-unit-control-button [command]="'stop'" [iconName]="'chrome-close'"
                               [disabled]="systemState === SystemState.Stopped"></app-unit-control-button>
    </div>
  `,
})
export class UnitControlsComponent {
  protected readonly SystemState = SystemState;
  protected systemState = this.store.select(DetailsSelectors.systemState);

  constructor(private store: Store) {}
}
