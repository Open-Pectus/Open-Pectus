import { ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, Output } from '@angular/core';
import { ProcessValue } from '../../api';

export interface PvAndPosition {
  processValue: ProcessValue,
  position: { x: number, y: number }
}

@Component({
  selector: 'app-process-value',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col md:flex-row bg-vscode-background-grey-hover p-1 md:p-1.5 items-center gap-1 md:gap-2 rounded select-none"
         [class.cursor-pointer]="hasCommands(processValue)" (click)="onClick()">
      <div class="mx-1 font-semibold">{{processValue?.name}}</div>
      <div class="bg-white rounded py-0.5 px-2 whitespace-nowrap min-h-[1.75rem] relative w-full md:w-auto text-center">
        {{processValue | processValue}}

        <div *ngIf="hasCommands(processValue)" [class.codicon-wand]="hasCommands(processValue)"
             class="absolute -top-1.5 -right-1 md:-right-1.5 p-[2.5px] codicon !text-[0.6rem] bg-vscode-background-grey-hover rounded-full"></div>
      </div>
    </div>
  `,
})
export class ProcessValueComponent {
  @Input() processValue?: ProcessValue;
  @Output() openCommands = new EventEmitter<PvAndPosition>();

  constructor(private element: ElementRef<HTMLDivElement>) {}

  onClick() {
    if(!this.hasCommands(this.processValue)) return;
    const domElement = this.element.nativeElement;
    const position = {x: domElement.offsetLeft + domElement.offsetWidth / 2, y: domElement.offsetTop + domElement.offsetHeight};
    const emitValue = {processValue: this.processValue, position};
    this.openCommands.emit(emitValue);
  }

  hasCommands(processValue?: ProcessValue): processValue is ProcessValue {
    return processValue?.commands !== undefined && processValue?.commands?.length !== 0;
  }
}
