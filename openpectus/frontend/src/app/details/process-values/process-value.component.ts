import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ProcessValue } from '../../api';

@Component({
  selector: 'app-process-value',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex bg-vscode-background-grey-hover p-2 items-center gap-2 rounded">
      <div class="mx-1 font-semibold">{{processValue?.name}}</div>
      <div class="bg-vscode-background-grey rounded py-0.5 px-1.5 whitespace-nowrap">
        {{processValue?.value}} {{processValue?.value_unit}}
      </div>
    </div>
  `,
})
export class ProcessValueComponent {
  @Input() processValue?: ProcessValue;


}
