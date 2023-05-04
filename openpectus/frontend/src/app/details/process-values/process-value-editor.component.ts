import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { ProcessValue, ProcessValueType } from '../../api';

export interface ValueAndUnit {
  value: string;
  unit?: string;
}

@Component({
  selector: 'app-process-value-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="absolute bg-sky-300 p-2 rounded-md top-8 left-1/2 -translate-x-1/2 flex shadow-lg shadow-gray-400">
      <input #inputElement class="p-1 outline-none rounded-l-sm w-32" type="text" [class.bg-red-500]="!isValid"
             (input)="onInput(inputElement.value)"
             [value]="processValueAsString(processValue)" (blur)="onBlur($event)" (keyup.enter)="onSaveInput(inputElement.value)">
      <button #saveButtonElement class="px-2.5 rounded-r bg-green-500 text-gray-900 font-semibold flex items-center gap-1.5"
              [class.bg-vscode-background-grey-hover]="!isValid"
              (click)="$event.stopPropagation(); onSaveInput(inputElement.value)" (blur)="onBlur($event)">
        <i class="codicon codicon-save"></i> Save
      </button>
    </div>
  `,
})
export class ProcessValueEditorComponent implements AfterViewInit {
  @Input() processValue?: ProcessValue;
  @ViewChild('inputElement', {static: false}) inputElement?: ElementRef<HTMLInputElement>;
  @ViewChild('saveButtonElement', {static: false}) saveButtonElement?: ElementRef<HTMLButtonElement>;
  @Output() shouldClose = new EventEmitter<ValueAndUnit | void>();

  isValid = true;

  processValueAsString(processValue: ProcessValue | undefined) {
    let string = processValue?.value?.toString();
    if(processValue?.value_unit !== undefined) string += ' ' + processValue?.value_unit;
    return string;
  }

  ngAfterViewInit() {
    this.inputElement?.nativeElement.focus();
    const valueLength = this.processValue?.value?.toString().length;
    if(valueLength !== undefined) this.inputElement?.nativeElement.setSelectionRange(0, valueLength);
  }

  toValueAndUnit(asString: string): ValueAndUnit | undefined {
    switch(this.processValue?.value_type) {
      case ProcessValueType.INT:
      case ProcessValueType.FLOAT:
        const matchArray = /^\s*(?<value>[0-9,.]+)\s*(?<unit>[^0-9,.]*)\s*$/.exec(asString);
        if(matchArray === null) return undefined;
        const [_, value, unit] = matchArray;
        return {value, unit};
      case ProcessValueType.STRING:
        return {value: asString};
      case undefined:
        return undefined;
    }
  }

  onSaveInput(value: string) {
    if(!this.isValid) return;
    this.shouldClose.emit(this.toValueAndUnit(value));

    // TODO: call backend through action/effect. This is just to show.
    if(this.processValue === undefined) return;
    this.processValue = {...this.processValue, value};
  }

  onBlur(event?: FocusEvent) {
    if(event?.relatedTarget === this.saveButtonElement?.nativeElement || event?.relatedTarget === this.inputElement?.nativeElement) return;
    this.shouldClose.emit();
  }

  onInput(value: string) {
    this.isValid = this.validate(value);
  }

  validate(value: string): boolean {
    const valueAndUnit = this.toValueAndUnit(value);
    if(valueAndUnit === undefined || this.processValue === undefined) return false;
    if(valueAndUnit.unit === undefined) return this.processValue.valid_value_units === undefined;
    return this.processValue.valid_value_units?.includes(valueAndUnit.unit) ?? false;
  }
}
