import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ProcessValue } from '../../api';
import { ValueAndUnit } from './process-value-editor.component';

@Component({
  selector: 'app-process-value',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex bg-vscode-background-grey-hover p-2 items-center gap-2 rounded" (dblclick)="onClick()">
      <div class="mx-1 font-semibold">{{processValue?.name}}</div>
      <div class="bg-vscode-background-grey rounded py-0.5 px-2 whitespace-nowrap min-h-[1.75rem] relative">
        {{processValue?.value}} {{processValue?.value_unit}}

        <div *ngIf="processValue?.writable"
             class="absolute -top-2 -right-2 p-[3px] codicon codicon-edit !text-[0.55rem] bg-vscode-background-grey-hover rounded-full"></div>

        <app-process-value-editor [processValue]="processValue" *ngIf="showEditor"
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
