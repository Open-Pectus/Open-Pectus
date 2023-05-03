import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsActions } from '../../ngrx/details.actions';
import { DetailsSelectors } from '../../ngrx/details.selectors';

@Component({
  selector: 'app-method-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col bg-sky-700 p-1.5 rounded-md m-6 shadow-lg">
      <div class="flex justify-between pb-2 m-2">

        <div class="flex gap-4">
          <span class="text-2xl font-bold text-gray-100">Method Editor</span>
          <button *ngIf="methodEditorIsDirty | ngrxPush" (click)="onSaveButtonClicked()"
                  class="bg-green-500 px-2.5 rounded-md codicon codicon-save font-bold !text-xl"></button>
        </div>

        <div class="flex gap-4">
          <!-- Buttons (Save, Examples/Methods, Commands) -->
          <button class="bg-green-500 px-4 rounded-md font-semibold text-gray-900">Examples</button>
          <button class="bg-green-500 px-4 rounded-md font-semibold text-gray-900">Commands</button>
        </div>
      </div>

      <app-monaco-editor class="h-96 rounded-sm overflow-hidden"></app-monaco-editor>
    </div>
  `,
})
export class MethodEditorComponent {
  methodEditorIsDirty = this.store.select(DetailsSelectors.methodEditorIsDirty);

  constructor(private store: Store) {}

  onSaveButtonClicked() {
    this.store.dispatch(DetailsActions.methodEditorModelSaveRequested());
  }
}
