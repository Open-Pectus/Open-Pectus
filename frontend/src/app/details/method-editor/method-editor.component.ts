import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, input, OnDestroy, OnInit } from '@angular/core';
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
  imports: [
    CollapsibleElementComponent,
    MonacoEditorComponent,
    PushPipe,
    NgIf,

  ],
  template: `
    <app-collapsible-element [name]="'Method Editor'" [heightResizable]="true" (contentHeightChanged)="onContentHeightChanged()"
                             [contentHeight]="400" (collapseStateChanged)="collapsed = $event" [codiconName]="'codicon-list-flat'">

      @if (!collapsed) {
        <div class="h-full flex flex-col" content>
          <div class="w-full bg-yellow-100 px-2 py-1.5 text-xs text-end border-b border-stone-100" *ngIf="versionMismatch | ngrxPush">
            {{ (method | ngrxPush)?.last_author }} has updated the method. You cannot save without refreshing first.
            <button class="bg-white rounded border-stone-300 border px-2 py-1 ml-2" (click)="forceRefreshMethod()">
              Discard my changes and refresh
            </button>
          </div>
          <app-monaco-editor class="block rounded-sm flex-1" [editorSizeChange]="editorSizeChange"
                             (keydown.control.s)="onCtrlS($event)"
                             [unitId]="unitId()"
                             [readOnlyEditor]="recentRunId() !== undefined"></app-monaco-editor>
        </div>
      }
      @if (!collapsed && (methodEditorIsDirty | ngrxPush)) {
        <button (click)="onSaveButtonClicked()" content
                class="bg-green-300 flex items-center text-black px-3 py-1.5 rounded-md absolute right-9 bottom-6 z-10">
          <span class="codicon codicon-save !text-lg"></span>
          <span class="ml-2">Save method</span>
        </button>
      }
    </app-collapsible-element>
  `,
})
export class MethodEditorComponent implements OnInit, OnDestroy {
  unitId = input<string>();
  recentRunId = input<string>();

  protected methodEditorIsDirty = this.store.select(MethodEditorSelectors.isDirty);
  protected versionMismatch = this.store.select(MethodEditorSelectors.versionMismatch);
  protected method = this.store.select(MethodEditorSelectors.method);
  protected editorSizeChange = new Subject<void>();
  protected collapsed = false;

  constructor(private store: Store) {}

  ngOnInit() {
    const unitId = this.unitId();
    const recentRunId = this.recentRunId();
    if(unitId !== undefined) {
      this.store.dispatch(MethodEditorActions.methodEditorComponentInitializedForUnit({unitId}));
    } else if(recentRunId !== undefined) {
      this.store.dispatch(MethodEditorActions.methodEditorComponentInitializedForRecentRun({recentRunId}));
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

  forceRefreshMethod() {
    const unitId = this.unitId();
    if(unitId === undefined) return;
    this.store.dispatch(MethodEditorActions.methodRefreshRequested({unitId}));
  }
}
