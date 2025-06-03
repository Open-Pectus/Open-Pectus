import { ChangeDetectionStrategy, Component, computed, input, OnDestroy, OnInit } from '@angular/core';
import { editor as MonacoEditor } from '@codingame/monaco-vscode-editor-api';
import { Store } from '@ngrx/store';
import { Subject } from 'rxjs';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { MethodEditorBehaviours } from './method-editor-behaviours';
import { MonacoEditorComponent } from './monaco-editor.component';
import { MethodEditorActions } from './ngrx/method-editor.actions';
import { MethodEditorSelectors } from './ngrx/method-editor.selectors';

@Component({
  selector: 'app-method-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CollapsibleElementComponent, MonacoEditorComponent],
  template: `
    <app-collapsible-element [name]="'Method Editor'" [heightResizable]="true" (contentHeightChanged)="onContentHeightChanged()"
                             [contentHeight]="400" (collapseStateChanged)="collapsed = $event" [codiconName]="'codicon-list-flat'">

      @if (!collapsed) {
        <div class="h-full flex flex-col" content>
          @if (versionMismatch()) {
            <div class="w-full bg-yellow-100 px-2 py-1.5 text-xs text-end border-b border-stone-100">
              {{ method().last_author }} has updated the method. You cannot save without refreshing first.
              <button class="bg-white rounded border-stone-300 border px-2 py-1 ml-2" (click)="forceRefreshMethod()">
                Discard my changes and refresh
              </button>
            </div>
          }
          <app-monaco-editor class="block rounded-sm flex-1 pl-1" [editorSizeChange]="editorSizeChange"
                             [unitId]="unitId()" (editorIsReady)="onEditorReady($event)"
                             [dropFileEnabled]="isStopped()" [dropFileDisabledReason]="dropFileDisabledReason"
                             [editorOptions]="editorOptions()"></app-monaco-editor>
        </div>
      }
      @if (!collapsed && methodEditorIsDirty()) {
        <button (click)="onSaveButtonClicked()" content [disabled]="versionMismatch()"
                class="bg-green-300 flex items-center text-black px-3 py-1.5 rounded-md absolute right-9 bottom-6 z-10"
                [class.!bg-gray-200]="versionMismatch()">
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

  protected methodEditorIsDirty = this.store.selectSignal(MethodEditorSelectors.isDirty);
  protected versionMismatch = this.store.selectSignal(MethodEditorSelectors.versionMismatch);
  protected method = this.store.selectSignal(MethodEditorSelectors.method);
  protected controlState = this.store.selectSignal(DetailsSelectors.controlState);
  protected isStopped = computed(() => !this.controlState().is_running);
  protected editorSizeChange = new Subject<void>();
  protected collapsed = false;
  protected editorOptions = computed(() => {
    return {readOnly: this.recentRunId() !== undefined, readOnlyMessage: {value: 'You cannot edit an already executed program'}};
  });
  private componentDestroyed = new Subject<void>();

  constructor(private store: Store) {}

  get dropFileDisabledReason() {
    if(this.recentRunId() !== undefined) return 'Cannot replace an already run program';
    if(!this.isStopped()) return 'Cannot replace a running program';
    return '';
  }

  ngOnInit() {
    const unitId = this.unitId();
    const recentRunId = this.recentRunId();
    if(unitId !== undefined) {
      this.store.dispatch(MethodEditorActions.methodEditorComponentInitializedForUnit({unitId}));
    } else if(recentRunId !== undefined) {
      this.store.dispatch(MethodEditorActions.methodEditorComponentInitializedForRecentRun({recentRunId}));
    }
  }

  onEditorReady(editor: MonacoEditor.IStandaloneCodeEditor) {
    new MethodEditorBehaviours(this.store, this.componentDestroyed, editor);
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
    this.store.dispatch(MethodEditorActions.methodEditorComponentDestroyed());
  }

  onSaveButtonClicked() {
    this.store.dispatch(MethodEditorActions.saveButtonClicked());
  }

  onContentHeightChanged() {
    this.editorSizeChange.next();
  }

  forceRefreshMethod() {
    const unitId = this.unitId();
    if(unitId === undefined) return;
    this.store.dispatch(MethodEditorActions.methodRefreshRequested({unitId}));
  }
}
