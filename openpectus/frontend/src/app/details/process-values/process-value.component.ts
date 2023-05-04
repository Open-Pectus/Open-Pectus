import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ProcessValue } from '../../api';
import { ValueAndUnit } from './process-value-editor.component';

@Component({
  selector: 'app-process-value',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex bg-vscode-background-grey-hover p-2 items-center gap-2 rounded">
      <div class="mx-1 font-semibold">{{processValue?.name}}</div>
      <div class="bg-vscode-background-grey rounded py-0.5 px-2 whitespace-nowrap" (click)="onClick()">
        {{processValue?.value}} {{processValue?.value_unit}}

        <app-process-value-editor [processValue]="processValue" class="relative" *ngIf="showEditor"
                                  (shouldClose)="onClose($event)"></app-process-value-editor>
      </div>
    </div>
  `,
})
export class ProcessValueComponent {
  @Input() processValue?: ProcessValue;

  showEditor = false;

  onClick() {
    if(!this.processValue?.writable) return;
    this.showEditor = true;
  }


  onClose(event: ValueAndUnit | void) {
    this.showEditor = false;
    if(event === undefined || this.processValue === undefined) return;
    this.processValue = {...this.processValue, value: event.value, value_unit: event.unit};
  }
}
