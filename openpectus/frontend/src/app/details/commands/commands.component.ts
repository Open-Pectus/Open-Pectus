import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { CommandExample } from '../../api/models/CommandExample';
import { CommandSource } from '../../api/models/CommandSource';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { CommandExamplesListComponent } from './command-examples-list.component';

@Component({
  selector: 'app-commands',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    CollapsibleElementComponent,
    NgIf,
    CommandExamplesListComponent,
    PushPipe,
  ],
  template: `
    <app-collapsible-element [name]="'Commands'" [heightResizable]="true" [contentHeight]="400" (collapseStateChanged)="collapsed = $event"
                             [codiconName]="'codicon-terminal'">
      <div content class="flex h-full overflow-x-auto" *ngIf="!collapsed">
        <app-command-examples-list [commandExamples]="commandExamples | ngrxPush" [chosenExample]="chosenExample"
                                   (exampleChosen)="chosenExample = $event"></app-command-examples-list>
        <div class="flex justify-between flex-1 relative">
          <textarea placeholder="Example to copy from" readonly
                    class="resize-none outline-none whitespace-pre flex-1 px-2 py-1.5 border-l border-r border-slate-500 -ml-[1px] min-w-[15rem]">{{ chosenExample?.example }}</textarea>
          <textarea #commandToExecute placeholder="Paste or write here to execute"
                    class="resize-none outline-none whitespace-pre flex-1 px-2 py-1.5 min-w-[15rem]"></textarea>
          <button class="absolute right-4 bottom-4 rounded-md bg-green-300 text-black px-3 py-2 flex items-center"
                  (click)="onExecute(commandToExecute.value); commandToExecute.value = ''">
            <i class="codicon codicon-symbol-event !text-black"></i>
            <span class="ml-1">Execute!</span>
          </button>
        </div>
      </div>
    </app-collapsible-element>
  `,
})
export class CommandsComponent implements OnInit {
  protected collapsed = false;
  protected commandExamples = this.store.select(DetailsSelectors.commandExamples);
  protected chosenExample?: CommandExample;

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
