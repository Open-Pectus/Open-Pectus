import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ProcessValue } from '../../api';

export enum AdditionalValueType {
  Start = 'start',
  End = 'end'
}

@Component({
  selector: 'app-run-log-additional-values',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div #additionalValues class="grid grid-rows-1 px-3 pb-2.5 gap-2.5 grid-flow-col justify-end items-center">
      <p class="text-xl font-semibold">{{type | titlecase}}:</p>
      <div *ngFor="let value of values; let valueIndex = index"
           class="border border-sky-700 rounded-md text-right overflow-hidden">
        <p class="text-white px-2 py-0.5"
           [class.bg-teal-700]="type === AdditionalValueType.Start"
           [class.bg-pink-900]="type === AdditionalValueType.End">
          {{value.name}}
        </p>
        <p class="px-2 py-0.5 bg-white ">{{value | processValue}}</p>
      </div>
    </div>
  `,
})
export class RunLogAdditionalValuesComponent {
  @Input() type?: AdditionalValueType;
  @Input() values?: ProcessValue[];
  protected readonly AdditionalValueType = AdditionalValueType;
}
