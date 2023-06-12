import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { CommandExample, CommandSource } from '../../api';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';

@Component({
  selector: 'app-commands',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Commands'" [heightResizable]="true" [contentHeight]="400">
      <div content class="flex h-full">
        <app-command-examples-list [commandExamples]="commandExamples | ngrxPush" [chosenExample]="chosenExample"
                                   (exampleChosen)="chosenExample = $event"></app-command-examples-list>
        <div class="flex justify-between flex-1 relative">
          <textarea class="resize-none outline-none whitespace-pre flex-1 px-2 py-1.5 border-l border-r border-slate-500 -ml-[1px]"
                    placeholder="Example to copy from" readonly>{{chosenExample?.example}}</textarea>
          <textarea class="resize-none outline-none whitespace-pre flex-1 px-2 py-1.5" #commandToExecute
                    placeholder="Paste or write here to execute"></textarea>
          <button class="absolute right-4 bottom-4 rounded-md bg-green-400 text-gray-800 p-2 flex items-center"
                  (click)="onExecute(commandToExecute.value); commandToExecute.value = ''">
            <div class="codicon codicon-symbol-event !text-gray-800"></div>
            <span class="font-semibold ml-1">Execute!</span>
          </button>
        </div>
      </div>
    </app-collapsible-element>
  `,
})
export class CommandsComponent implements OnInit {
  commandExamples = this.store.select(DetailsSelectors.commandExamples);
  chosenExample?: CommandExample;

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.commandsComponentInitialized());
  }

  onExecute(commandToExecute: string) {
    this.store.dispatch(DetailsActions.commandsComponentExecuteClicked({
      command: {
        command: commandToExecute,
        source: CommandSource.MANUALLY_ENTERED,
      },
    }));
  }
}
