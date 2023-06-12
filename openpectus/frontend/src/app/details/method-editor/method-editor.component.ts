import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { Subject } from 'rxjs';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';

@Component({
  selector: 'app-method-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Method Editor'" [heightResizable]="true" (contentHeightChanged)="onContentHeightChanged()"
                             [contentHeight]="400">
      <button *ngIf="methodEditorIsDirty | ngrxPush" (click)="onSaveButtonClicked()"
              class="bg-green-500 flex items-center text-slate-800 px-2.5 rounded-md">
        <span class="codicon codicon-save !text-xl"></span>
        <span class="ml-2 font-semibold">Save</span>
      </button>
      <app-monaco-editor class="block rounded-sm h-full" [editorSizeChange]="editorSizeChange"
                         content></app-monaco-editor>
    </app-collapsible-element>
  `,
})
export class MethodEditorComponent {
  methodEditorIsDirty = this.store.select(DetailsSelectors.methodEditorIsDirty);
  editorSizeChange = new Subject<void>();

  constructor(private store: Store) {}

  onSaveButtonClicked() {
    this.store.dispatch(DetailsActions.methodEditorModelSaveRequested());
  }

  onContentHeightChanged() {
    this.editorSizeChange.next();
  }
}
