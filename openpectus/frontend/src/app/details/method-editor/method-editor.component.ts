import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-method-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col bg-vscode-background-grey p-2 rounded-lg m-6">
      <!-- Title, Buttons (Save, Examples/Methods, Commands) -->
      <span class="text-2xl font-bold mb-2 text-gray-600">Method Editor</span>
      <app-monaco-editor class="h-96"></app-monaco-editor>
    </div>
  `,
})
export class MethodEditorComponent {

}
