import { ChangeDetectionStrategy, Component, forwardRef, input, signal } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

export interface MultiSelectOption {
  value: string;
  name: string;
}

@Component({
  selector: 'app-multi-select',
  providers: [{provide: NG_VALUE_ACCESSOR, useExisting: forwardRef(() => MultiSelectComponent), multi: true}],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col gap-0.5" (focus)="onTouchCallback?.()">
      @for (option of options(); track option.value) {
        <label class="flex items-center gap-2">
          <input type="checkbox" class="w-5 h-5 accent-blue-500"
                 [checked]="controlValue().includes(option.value)"
                 (change)="onChange(option.value, $event)">
          {{ option.name }}
        </label>
      }
    </div>
  `,
})
export class MultiSelectComponent implements ControlValueAccessor {
  options = input.required<MultiSelectOption[]>();
  protected controlValue = signal<string[]>([]);
  protected onChangeCallback?: (value: string[]) => void;
  protected onTouchCallback?: () => void;

  writeValue(value: string[]): void {
    this.controlValue.set(value);
  }

  registerOnChange(onChange: (value: string[]) => void): void {
    this.onChangeCallback = onChange;
  }

  registerOnTouched(onTouched: () => void): void {
    this.onTouchCallback = onTouched;
  }

  onChange(optionValue: string, event: Event) {
    const checked = (event.target as HTMLInputElement).checked;
    const newValue = checked ? [...this.controlValue(), optionValue] : this.controlValue().filter(value => value !== optionValue);
    this.controlValue.set(newValue);
    this.onChangeCallback?.(newValue);
  }
}
