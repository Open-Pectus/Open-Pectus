import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { CommandExample } from '../api';
import { DetailsActions } from './ngrx/details.actions';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-commands',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Commands'" [collapsed]="false">
      <div content class="flex m-2 max-h-72 bg-vscode-background-grey">
        <div class="flex flex-col gap-1 max-w-[16rem] overflow-y-auto -my-2 py-2" [style.scrollbar-width]="'none'">
          <button *ngFor="let commandExample of commandExamples | ngrxPush"
                  class="rounded-l-xl p-2 bg-vscode-background-grey-hover select-none border border-slate-500 border-r-0"
                  [class.!bg-white]="commandExample === chosenExample"
                  [class.z-10]="commandExample === chosenExample"
                  (click)="chosenExample = commandExample">
            {{commandExample.name}}
          </button>
        </div>
        <div class="flex justify-between flex-1 relative">
          <textarea class="resize-none outline-none whitespace-pre flex-1 p-2 border border-slate-500 -ml-[1px]"
                    placeholder="Example to copy from">{{chosenExample?.example}}</textarea>
          <textarea class="resize-none outline-none p-2 flex-1"
                    placeholder="Paste or write here to execute"></textarea>
          <button class="absolute right-2 bottom-2 rounded bg-green-400 text-gray-800 p-2 flex items-center" (click)="onExecute()">
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

  onExecute() {
    // TODO
  }
}
