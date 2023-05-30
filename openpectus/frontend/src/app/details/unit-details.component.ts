import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { CommandSource, ExecutableCommand } from '../api';
import { DetailsActions } from './ngrx/details.actions';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-unit-details',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex justify-center">
      <div class="flex flex-col max-w-5xl w-full p-8 gap-8">
        <div class="flex justify-between items-start gap-4">
          <div class="text-slate-700" *ngrxLet="processUnit as processUnit">
            <h1 class="text-4xl font-bold">{{processUnit?.name}}</h1>
            <span class="text-sm">{{processUnit?.current_user_role}}</span>
          </div>

          <div class="flex gap-2.5">
            <button *ngFor="let command of controlCommands"
                    class="py-2 px-4 rounded-lg text-white bg-slate-700 flex items-center gap-1"
                    (click)="executeCommand(command)">
              <span class="codicon" [ngClass]="'codicon-'+getIcon(command)"></span>{{command.name}}
            </button>
          </div>
        </div>
        <app-process-values></app-process-values>
        <app-method-editor></app-method-editor>
        <app-commands></app-commands>
        <!-- Plot -->
        <app-process-diagram></app-process-diagram>
      </div>
    </div>
  `,
})
export class UnitDetailsComponent {
  processUnit = this.store.select(DetailsSelectors.processUnit);

  protected readonly controlCommands: ExecutableCommand[] = [{
    command: 'start',
    name: 'Start',
    source: CommandSource.UNIT_BUTTON,
  }, {
    command: 'pause',
    name: 'Pause',
    source: CommandSource.UNIT_BUTTON,
  }, {
    command: 'hold',
    name: 'Hold',
    source: CommandSource.UNIT_BUTTON,
  }, {
    command: 'stop',
    name: 'Stop',
    source: CommandSource.UNIT_BUTTON,
  }];

  constructor(private store: Store) {}

  getIcon(command: ExecutableCommand) {
    switch(command.name) {
      case 'Start':
        return 'play';
      case 'Pause':
        return 'debug-pause';
      case 'Hold':
        return 'debug-stop';
      case 'Stop':
        return 'chrome-close';
      default:
        return '';
    }
  }

  executeCommand(command: ExecutableCommand) {
    this.store.dispatch(DetailsActions.processUnitCommandButtonClicked({command}));
  }
}
