import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { Subject } from 'rxjs';
import { CommandExample } from '../../api';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { MonacoEditorComponent } from '../method-editor/monaco-editor.component';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { CommandExamplesListComponent } from './command-examples-list.component';

@Component({
  selector: 'app-commands',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CollapsibleElementComponent, CommandExamplesListComponent, MonacoEditorComponent],
  template: `
    <app-collapsible-element [name]="'Commands'" [heightResizable]="true" [contentHeight]="400" (collapseStateChanged)="collapsed = $event"
                             [codiconName]="'codicon-terminal'" (contentHeightChanged)="onContentHeightChanged()">
      @if (!collapsed) {
        <div content class="flex h-full overflow-x-auto">
          <app-command-examples-list [commandExamples]="commandExamples()" [chosenExample]="chosenExample"
                                     (exampleChosen)="chosenExample = $event"></app-command-examples-list>
          <div class="flex justify-between flex-1 relative">
            <textarea placeholder="Example to copy from" readonly
                      class="resize-none outline-none whitespace-pre flex-1 px-2 py-1.5 border-l border-r border-slate-500 -ml-[1px] min-w-[15rem]">{{ chosenExample?.example }}</textarea>
            <app-monaco-editor [editorSizeChange]="editorSizeChange" (editorContentChanged)="onEditorContentChanged($event)"
                               [editorContent]="commandToExecute" [unitId]="unitId()"
                               class="flex-1 min-w-[15rem] pl-1"></app-monaco-editor>
            <button class="absolute right-4 bottom-4 rounded-md bg-green-300 text-black px-3 py-2 flex items-center"
                    (click)="onExecute()">
              <i class="codicon codicon-symbol-event !text-black"></i>
              <span class="ml-1">Execute!</span>
            </button>
          </div>
        </div>
      }
    </app-collapsible-element>
  `,
})
export class CommandsComponent implements OnInit {
  protected collapsed = false;
  protected commandExamples = this.store.selectSignal(DetailsSelectors.commandExamples);
  protected unitId = this.store.selectSignal(DetailsSelectors.processUnitId);
  protected chosenExample?: CommandExample;
  protected editorSizeChange = new Subject<void>();
  protected commandToExecute = '';

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.commandsComponentInitialized());
  }

  onExecute() {
    this.store.dispatch(DetailsActions.commandsComponentExecuteClicked({
      command: {
        command: this.commandToExecute,
        source: 'manually_entered',
      },
    }));
    this.commandToExecute = '';
  }

  onContentHeightChanged() {
    this.editorSizeChange.next();
  }

  onEditorContentChanged(lines: string[]) {
    this.commandToExecute = lines.join('\n');
  }
}
