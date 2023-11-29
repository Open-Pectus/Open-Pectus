import { NgFor } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ProcessValue } from '../../api';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';

export enum AdditionalValueType {
  Start = 'start',
  End = 'end'
}

@Component({
  selector: 'app-run-log-additional-values',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div #additionalValues class="grid grid-rows-1 px-3 pb-2.5 gap-2.5 grid-flow-col justify-end items-center">
      <p class="text-sm">At {{type}}:</p>
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
  standalone: true,
  imports: [NgFor, ProcessValuePipe],
})
export class RunLogAdditionalValuesComponent {
  @Input() type?: AdditionalValueType;
  @Input() values?: ProcessValue[];
  protected readonly AdditionalValueType = AdditionalValueType;
}
