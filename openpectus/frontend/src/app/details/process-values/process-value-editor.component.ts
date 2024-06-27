import { ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { ProcessValueCommand } from '../../api/models/ProcessValueCommand';
import { ProcessValueCommandChoiceValue } from '../../api/models/ProcessValueCommandChoiceValue';
import { ProcessValueCommandFreeTextValue } from '../../api/models/ProcessValueCommandFreeTextValue';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';

export interface ValueAndUnit {
  value: string;
  unit?: string;
}

@Component({
  selector: 'app-process-value-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [ProcessValuePipe],
  template: `
    <div class="flex">
      <input #inputElement class="p-1 pl-2 outline-none border-l border-y border-gray-300 rounded-l-md w-32" type="text"
             [class.bg-red-500]="!isValid"
             (input)="onInput(inputElement.value)" (blur)="inputBlur.emit($event)"
             [value]="command?.value | processValue" (focus)="onFocusInput()"
             (keyup.enter)="onSaveInput(inputElement.value)">
      <button #saveButtonElement class="px-3 py-2 rounded-r-md bg-green-400 text-gray-800 font-semibold"
              [class.bg-vscode-background-grey-hover]="!isValid" tabindex="-1"
              (click)="$event.stopPropagation(); onSaveInput(inputElement.value)">
        {{ command?.name }}
      </button>
    </div>
  `,
})
export class ProcessValueEditorComponent {
  @Input() command?: ProcessValueCommand;
  @ViewChild('inputElement', {static: false}) inputElement?: ElementRef<HTMLInputElement>;
  @ViewChild('saveButtonElement', {static: false}) saveButtonElement?: ElementRef<HTMLButtonElement>;
  @Output() save = new EventEmitter<ValueAndUnit | undefined>();
  @Output() inputBlur = new EventEmitter<FocusEvent>();

  isValid = true;

  constructor(private processValuePipe: ProcessValuePipe) {}

  focus() {
    this.inputElement?.nativeElement.focus();
  }

  onFocusInput() {
    if(this.command?.value?.value_type === ProcessValueCommandFreeTextValue.value_type.STRING) return this.inputElement?.nativeElement.select();
    const formattedValue = this.processValuePipe.transform(this.command?.value);
    const valueLength = formattedValue?.indexOf(' ');
    if(valueLength !== undefined) this.inputElement?.nativeElement.setSelectionRange(0, valueLength);
  }

  toValueAndUnit(asString: string): ValueAndUnit | undefined {
    switch(this.command?.value?.value_type) {
      case 'int':
      case 'float':
        const matchArray = /^\s*(?<value>[0-9,.]+)\s*(?<unit>[^0-9,.]*)\s*$/.exec(asString);
        if(matchArray === null) return undefined;
        const [_, value, unit] = matchArray;
        return {value, unit};
      case ProcessValueCommandFreeTextValue.value_type.STRING:
        return {value: asString};
      case ProcessValueCommandChoiceValue.value_type.CHOICE:
        return {value: asString}; // TODO: probably not right
      case undefined:
        return undefined;
    }
  }

  onSaveInput(value?: string) {
    if(!this.isValid) return;
    if(value !== undefined) return this.save.emit(this.toValueAndUnit(value));
    this.save.emit();
  }

  onInput(value: string) {
    this.isValid = this.validate(value);
  }

  validate(value: string): boolean {
    const valueAndUnit = this.toValueAndUnit(value);
    if(valueAndUnit === undefined || this.command === undefined) return false;
    if(this.command?.value?.value_type === 'int' || this.command?.value?.value_type === 'float') {
      if(valueAndUnit.unit === undefined) return false;
      return this.command?.value?.valid_value_units?.includes(valueAndUnit.unit) ?? false;
    }
    return true;
  }
}
