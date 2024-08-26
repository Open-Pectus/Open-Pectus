import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { DetailsQueriesService } from '../details-queries.service';
import { UnitControlButtonComponent } from './unit-control-button.component';


@Component({
  selector: 'app-unit-controls',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [LetDirective, UnitControlButtonComponent],
  template: `
    <div class="flex gap-3.5 flex-wrap">
      <app-unit-control-button [command]="'Start'" [iconName]="'play'" [toggledColor]="startColor"
                               [toggled]="controlStateQuery.data()?.is_running ?? false"></app-unit-control-button>
      <app-unit-control-button [command]="'Pause'" [iconName]="'debug-pause'"
                               [unCommand]="'Unpause'" [toggledColor]="pauseColor"
                               [toggled]="controlStateQuery.data()?.is_paused ?? false"></app-unit-control-button>
      <app-unit-control-button [command]="'Hold'" [iconName]="'debug-stop'"
                               [unCommand]="'Unhold'" [toggledColor]="pauseColor"
                               [toggled]="controlStateQuery.data()?.is_holding ?? false"></app-unit-control-button>
      <app-unit-control-button [command]="'Stop'" [iconName]="'chrome-close'" [toggledColor]="stopColor"
                               [toggled]="!controlStateQuery.data()?.is_running"></app-unit-control-button>
    </div>
  `,
})
export class UnitControlsComponent {
  engineId = input.required<string>();
  readonly startColor = '#047857';
  readonly pauseColor = '#ca8a04';
  readonly stopColor = '#b91c1c';
  protected controlStateQuery = this.detailsQueriesService.injectControlStateQuery();

  constructor(private detailsQueriesService: DetailsQueriesService) {}
}
