import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input, OnDestroy, OnInit } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { Subject } from 'rxjs';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { MonacoEditorComponent } from './monaco-editor.component';
import { MethodEditorActions } from './ngrx/method-editor.actions';
import { MethodEditorSelectors } from './ngrx/method-editor.selectors';

@Component({
  selector: 'app-method-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    CollapsibleElementComponent,
    NgIf,
    MonacoEditorComponent,
    PushPipe,
  ],
  template: `
    <app-collapsible-element [name]="'Method Editor'" [heightResizable]="true" (contentHeightChanged)="onContentHeightChanged()"
                             [contentHeight]="400" (collapseStateChanged)="collapsed = $event" [codiconName]="'codicon-list-flat'">
      <button *ngIf="methodEditorIsDirty | ngrxPush" (click)="onSaveButtonClicked()" buttons
              class="bg-green-400 flex items-center text-gray-800 px-2.5 rounded-md">
        <span class="codicon codicon-save !text-xl"></span>
        <span class="ml-2 font-semibold">Save</span>
      </button>
      <app-monaco-editor class="block rounded-sm h-full" [editorSizeChange]="editorSizeChange"
                         content *ngIf="!collapsed" (keydown.control.s)="onCtrlS($event)"
                         [readOnlyEditor]="recentRunId !== undefined"></app-monaco-editor>
    </app-collapsible-element>
  `,
})
export class MethodEditorComponent implements OnInit, OnDestroy {
  @Input() unitId?: string;
  @Input() recentRunId?: string;

  protected methodEditorIsDirty = this.store.select(MethodEditorSelectors.isDirty);
  protected editorSizeChange = new Subject<void>();
  protected collapsed = false;

  constructor(private store: Store) {}

  ngOnInit() {
    if(this.unitId !== undefined) {
      this.store.dispatch(MethodEditorActions.methodEditorComponentInitializedForUnit({unitId: this.unitId}));
    } else if(this.recentRunId !== undefined) {
      this.store.dispatch(MethodEditorActions.methodEditorComponentInitializedForRecentRun({recentRunId: this.recentRunId}));
    }
  }

  ngOnDestroy() {
    this.store.dispatch(MethodEditorActions.methodEditorComponentDestroyed());
  }

  onSaveButtonClicked() {
    this.store.dispatch(MethodEditorActions.saveButtonClicked());
  }

  onContentHeightChanged() {
    this.editorSizeChange.next();
  }

  onCtrlS(event: Event) {
    event.preventDefault();
    event.stopPropagation();
    this.store.dispatch(MethodEditorActions.saveKeyboardShortcutPressed());
  }
}
