import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { ProcessValue } from '../../api';

export interface ValueAndUnit {
  value: string;
  unit: string;
}

@Component({
  selector: 'app-process-value-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="absolute bg-sky-300 p-2 rounded-md top-1 left-1/2 -translate-x-1/2 flex shadow-lg shadow-gray-400">
      <input #inputElement class="p-1 outline-none rounded-l-sm w-32" type="text"
             [value]="processValueAsString(processValue)" (blur)="onBlur($event)" (keyup.enter)="onSaveInput(inputElement.value)">
      <button #saveButtonElement class="px-2.5 rounded-r bg-green-500 text-gray-900 font-semibold flex items-center gap-1.5"
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
  }

  toValueAndUnit(asString: string): ValueAndUnit {
    const matchArray = /^\s*(?<value>[0-9,.]+)\s*(?<unit>[^0-9,.]*)\s*$/.exec(asString);
    if(matchArray === null) {
      this.isValid = false;
      return {value: asString, unit: ''};
    }
    const [_, value, unit] = matchArray;
    if(!this.processValue?.value_unit?.includes(unit)) this.isValid = false;
    return {value, unit};
  }

  onSaveInput(value: string) {
    this.shouldClose.emit(this.toValueAndUnit(value));

    // TODO: call backend through action/effect. This is just to show.
    if(this.processValue === undefined) return;
    this.processValue = {...this.processValue, value};
  }

  onBlur(event?: FocusEvent) {
    if(event?.relatedTarget === this.saveButtonElement?.nativeElement || event?.relatedTarget === this.inputElement?.nativeElement) return;
    this.shouldClose.emit();
  }
}
