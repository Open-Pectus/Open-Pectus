import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-toggle-button',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <label class="flex items-center gap-1 cursor-pointer rounded px-2 bg-slate-50 border-gray-300 border !text-black h-8">
      {{ label }}
      <input type="checkbox" (change)="checked = checkbox.checked; changed.emit(checkbox.checked)" #checkbox [checked]="checked"
             [class.codicon-pass]="checked" [class.codicon-circle-large]="!checked"
             class="w-5 !text-xl appearance-none font-bold codicon cursor-pointer">
    </label>
  `,
})
export class ToggleButtonComponent {
  @Input() checked?: boolean;
  @Input() label?: string;
  @Output() changed = new EventEmitter<boolean>();
}
