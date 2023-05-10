import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { ProcessValue, ProcessValueCommand } from '../../api';
import { DetailsActions } from '../ngrx/details.actions';
import { ValueAndUnit } from './process-value-editor.component';

@Component({
  selector: 'app-process-value',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex bg-vscode-background-grey-hover p-2 items-center gap-2 rounded select-none"
         [class.cursor-pointer]="hasAction(processValue)" (click)="onClick()">
      <div class="mx-1 font-semibold">{{processValue?.name}}</div>
      <div class="bg-vscode-background-grey rounded py-0.5 px-2 whitespace-nowrap min-h-[1.75rem] relative">
        {{processValue?.value}} {{processValue?.value_unit}}

        <div *ngIf="hasAction(processValue)"
             [class.codicon-edit]="processValue?.writable" [class.codicon-wand]="hasCommands(processValue)"
             class="absolute -top-2 -right-2 p-[2.5px] codicon !text-[0.6rem] bg-vscode-background-grey-hover rounded-full"></div>

        <app-process-value-editor [processValue]="processValue" *ngIf="showEditor"
                                  (shouldClose)="onCloseEditor($event)"></app-process-value-editor>
        <app-process-value-commands *ngIf="showCommands" [processValueCommands]="processValue?.commands"
                                    (shouldClose)="onCloseCommands($event)"></app-process-value-commands>
      </div>
    </div>
  `,
})
export class ProcessValueComponent {
  @Input() processValue?: ProcessValue;
  protected showEditor = false;
  protected showCommands = false;

  constructor(private store: Store) {}

  onClick() {
    if(this.processValue?.writable) this.showEditor = true;
    if(this.processValue?.commands !== undefined && this.processValue?.commands.length !== 0) this.showCommands = true;
  }

  onCloseCommands(command?: ProcessValueCommand) {
    this.showCommands = false;
    if(command === undefined || this.processValue === undefined) return;
    this.store.dispatch(DetailsActions.processValueCommandClicked({processValueName: this.processValue.name, command: command}));
  }

  onCloseEditor(valueAndUnit?: ValueAndUnit) {
    this.showEditor = false;
    if(valueAndUnit === undefined || this.processValue === undefined) return;
    // TODO: Call backend instead, this is just for show, for now.
    this.processValue = {...this.processValue, value: valueAndUnit.value, value_unit: valueAndUnit.unit};
  }

  hasCommands(processValue?: ProcessValue) {
    return processValue?.commands !== undefined && processValue?.commands?.length !== 0;
  }

  hasAction(processValue?: ProcessValue) {
    return processValue?.writable || this.hasCommands(processValue);
  }
}
