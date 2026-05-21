import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { ProcessValue } from '../../api';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';

export enum AdditionalValueType {
  Start = 'start',
  End = 'end'
}

@Component({
  selector: 'app-run-log-additional-values',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ProcessValuePipe],
  template: `
    <div #additionalValues class="flex flex-wrap px-3 pb-2.5 gap-2.5 justify-end items-start">
      <p class="text-sm">At {{ type() }}:</p>
      @for (value of values(); track value; let valueIndex = $index) {
        <div
            class="border border-sky-700 rounded-md text-right overflow-hidden">
          <p class="text-white px-2 py-0.5"
             [class.bg-teal-700]="type() === AdditionalValueType.Start"
             [class.bg-pink-900]="type() === AdditionalValueType.End">
            {{ value.name }}
          </p>
          <p class="px-2 py-0.5 bg-white ">{{ value | processValue }}</p>
        </div>
      }
    </div>
  `
})
export class RunLogAdditionalValuesComponent {
  readonly type = input<AdditionalValueType>();
  readonly values = input<ProcessValue[]>();
  protected readonly AdditionalValueType = AdditionalValueType;
}
