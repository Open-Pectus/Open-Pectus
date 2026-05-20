import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';

@Component({
  selector: 'app-toggle-button',
  imports: [],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <label class="flex items-center gap-1 cursor-pointer rounded px-2 bg-gray-50 border-gray-300 border !text-black h-8">
      {{ label() }}
      <input type="checkbox" (change)="changed.emit(checkbox.checked)" #checkbox [checked]="checked()"
             [class.codicon-pass]="checkbox.checked" [class.codicon-circle-large]="!checkbox.checked"
             class="w-5 !text-xl appearance-none font-bold codicon cursor-pointer">
    </label>
  `
})
export class ToggleButtonComponent {
  readonly checked = input<boolean>();
  readonly label = input<string>();
  readonly changed = output<boolean>();
}
