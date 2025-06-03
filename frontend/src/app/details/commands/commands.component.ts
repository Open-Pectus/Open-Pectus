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
        <div content class="grid grid-cols-[14rem_minmax(0,1fr)_1px_minmax(0,1fr)] grid-rows-[100%] h-full">
          <app-command-examples-list class="overflow-y-hidden" [commandExamples]="commandExamples()" [chosenExample]="chosenExample"
                                     (exampleChosen)="chosenExample = $event"></app-command-examples-list>
          <app-monaco-editor [editorSizeChange]="editorSizeChange" [editorOptions]="exampleEditorOptions"
                             [editorContent]="chosenExampleContent"
                             [dropFileDisabledReason]="'Cannot change example content'"
                             class="ml-1"></app-monaco-editor>
          <div class="h-full w-[1px] bg-slate-500"></div>
          <app-monaco-editor [editorSizeChange]="editorSizeChange" (editorContentChanged)="onEditorContentChanged($event)"
                             [editorContent]="commandToExecute" [unitId]="unitId()"
                             [dropFileEnabled]="true"
                             class="ml-1"></app-monaco-editor>
          <button class="absolute right-4 bottom-4 rounded-md bg-green-300 text-black px-3 py-2 flex items-center"
                  (click)="onExecute()">
            <i class="codicon codicon-symbol-event !text-black"></i>
            <span class="ml-1">Execute!</span>
          </button>
        </div>
      }
    </app-collapsible-element>
  `,
})
export class CommandsComponent implements OnInit {
  protected exampleEditorOptions = {readOnly: true, readOnlyMessage: {value: 'You cannot edit an example'}};
  protected collapsed = false;
  protected commandExamples = this.store.selectSignal(DetailsSelectors.commandExamples);
  protected unitId = this.store.selectSignal(DetailsSelectors.processUnitId);
  protected chosenExample?: CommandExample;
  protected editorSizeChange = new Subject<void>();
  protected commandToExecute = '';

  constructor(private store: Store) {}

  get chosenExampleContent() {
    return this.chosenExample?.example; // doing this in getter instead of template, because ?. in template can apparently return null.
    // See also https://github.com/angular/angular/issues/37622 and https://github.com/angular/angular/pull/37747
  }

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
