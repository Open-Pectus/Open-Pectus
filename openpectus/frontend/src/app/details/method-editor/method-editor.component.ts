import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';

@Component({
  selector: 'app-method-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Method Editor'">
      <button *ngIf="methodEditorIsDirty | ngrxPush" (click)="onSaveButtonClicked()"
              class="bg-green-500 flex items-center text-gray-700 px-2.5 rounded-md">
        <span class="codicon codicon-save !text-xl"></span>
        <span class="ml-2 font-semibold">Save</span>
      </button>
      <app-monaco-editor class="block h-[400px] rounded-sm overflow-hidden" content></app-monaco-editor>
    </app-collapsible-element>
  `,
})
export class MethodEditorComponent {
  methodEditorIsDirty = this.store.select(DetailsSelectors.methodEditorIsDirty);

  constructor(private store: Store) {}

  onSaveButtonClicked() {
    this.store.dispatch(DetailsActions.methodEditorModelSaveRequested());
  }
}
