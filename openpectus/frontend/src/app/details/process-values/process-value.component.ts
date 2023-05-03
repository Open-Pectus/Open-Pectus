import { ChangeDetectionStrategy, Component, ElementRef, Input, ViewChild } from '@angular/core';
import { ProcessValue, ProcessValueType } from '../../api';
import { UtilMethods } from '../../shared/util-methods';

@Component({
  selector: 'app-process-value',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex bg-vscode-background-grey-hover p-2 items-center gap-2 rounded">
      <div class="mx-1 font-semibold">{{processValue?.name}}</div>
      <div class="bg-vscode-background-grey rounded py-0.5 px-2 whitespace-nowrap" (click)="onClick()">
        {{processValue?.value}} {{processValue?.value_unit}}

        <div class="relative" *ngIf="showInput">
          <div class="absolute bg-sky-300 p-2 rounded-md top-1 left-1/2 -translate-x-1/2 flex shadow-lg shadow-gray-400">
            <input #inputElement class="p-1 outline-none rounded-l-sm w-32" [type]="inputType" [value]="processValue?.value"
                   (blur)="onBlur($event)"
                   (keyup.enter)="onSaveInput(inputElement.value)">
            <button #saveButtonElement class="px-2.5 rounded-r bg-green-500 text-gray-900 font-semibold flex items-center gap-1.5"
                    (click)="$event.stopPropagation(); onSaveInput(inputElement.value)" (blur)="onBlur($event)">
              <i class="codicon codicon-save"></i> Save
            </button>
          </div>
        </div>

      </div>
    </div>
  `,
})
export class ProcessValueComponent {
  @Input() processValue?: ProcessValue;
  @ViewChild('inputElement', {static: false}) inputElement?: ElementRef<HTMLInputElement>;
  @ViewChild('saveButtonElement', {static: false}) saveButtonElement?: ElementRef<HTMLButtonElement>;

  showInput = false;

  get inputType() {
    const valueType = this.processValue?.value_type;
    switch(valueType) {
      case undefined:
        return undefined;
      case ProcessValueType.INT:
      case ProcessValueType.FLOAT:
        return 'number';
      case ProcessValueType.STRING:
        return 'text';
      default:
        UtilMethods.assertNever(valueType);
    }
  }

  onClick() {
    if(!this.processValue?.writable) return;
    this.showInput = true;
    setTimeout(() => this.inputElement?.nativeElement.focus());
  }

  onSaveInput(value: string) {
    this.showInput = false;

    // TODO: call backend through action/effect. This is just to show.
    if(this.processValue === undefined) return;
    this.processValue = {...this.processValue, value};
  }

  onBlur(event?: FocusEvent) {
    if(event?.relatedTarget === this.saveButtonElement?.nativeElement || event?.relatedTarget === this.inputElement?.nativeElement) return;
    this.showInput = false;
  }
}
