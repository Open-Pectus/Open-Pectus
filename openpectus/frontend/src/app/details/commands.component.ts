import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { CommandExample, CommandSource } from '../api';
import { DetailsActions } from './ngrx/details.actions';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-commands',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Commands'" [collapsed]="false">
      <div content class="flex m-2 max-h-96 bg-vscode-background-grey">
        <div class="flex flex-col gap-1 max-w-[16rem] overflow-y-auto -my-2 py-2" [style.scrollbar-width]="'none'">
          <button *ngFor="let commandExample of commandExamples | ngrxPush"
                  class="rounded-l-2xl p-2 bg-slate-200 select-none border border-r-0 border-slate-500"
                  [class.!bg-white]="commandExample === chosenExample"
                  [class.z-10]="commandExample === chosenExample"
                  (click)="chosenExample = commandExample">
            {{commandExample.name}}
          </button>
        </div>
        <div class="flex justify-between flex-1 relative">
          <div class="h-full absolute -left-0.5 top-0 w-0.5 bg-gradient-to-r from-transparent to-slate-500"></div>
          <!--          <svg viewBox="0 0 9 9" width="9" height="9" class="w-[9px] h-[9px] absolute -top-[8px] -left-[1px] stroke-slate-500">-->
          <!--            <path stroke="white" stroke-width="1" d="M0,8.5H9"></path>-->
          <!--            <path fill="none" stroke-width="1" d="M0.5,0V9M0.5,0A8.5,8.5,0,0,0,9,8.5"></path>-->
          <!--          </svg>-->

          <textarea class="resize-none outline-none whitespace-pre flex-1 px-2 border border-slate-500 -ml-[1px] rounded-r-lg"
                    placeholder="Example to copy from" readonly>{{chosenExample?.example}}</textarea>
          <textarea class="resize-none outline-none whitespace-pre flex-1 px-2" #commandToExecute
                    placeholder="Paste or write here to execute"></textarea>
          <button class="absolute right-1 bottom-1 rounded bg-green-400 text-gray-800 p-2 flex items-center"
                  (click)="onExecute(commandToExecute.value)">
            <div class="codicon codicon-symbol-event"></div>
            <span>Execute!</span>
          </button>
        </div>
      </div>
    </app-collapsible-element>
  `,
  styles: [
    '::-webkit-scrollbar { display: none; }',
  ],
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
