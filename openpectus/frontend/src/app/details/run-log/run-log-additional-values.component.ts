import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ProcessValue } from '../../api';

@Component({
  selector: 'app-run-log-additional-values',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div #additionalValues class="grid grid-rows-1 px-2 grid-flow-col justify-end items-center">
      <p class="mb-2 mx-2 text-xl font-semibold">{{name}}:</p>
      <div *ngFor="let value of values; let valueIndex = index"
           class="mx-2 mb-2 border border-sky-700 rounded-md text-right overflow-hidden">
        <p class="bg-sky-700 text-white px-2 py-0.5">{{value.name}}</p>
        <p class="px-2 py-0.5 bg-white ">{{value | processValue}}</p>
      </div>
    </div>
  `,
})
export class RunLogAdditionalValuesComponent {
  @Input() name?: string;
  @Input() values?: ProcessValue[];
}
