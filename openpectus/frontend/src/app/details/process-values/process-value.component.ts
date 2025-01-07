import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, Output } from '@angular/core';
import { ProcessValue } from '../../api';
import { ProcessValuePipe } from '../../shared/pipes/process-value.pipe';

export interface PvAndPosition {
  processValue: ProcessValue,
  position: { x: number, y: number }
}

@Component({
    selector: 'app-process-value',
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [NgIf, ProcessValuePipe],
    template: `
    <div class="flex flex-col bg-sky-200 p-0.5 items-center gap-1 rounded select-none border border-sky-300"
         [class.cursor-pointer]="hasCommands(processValue)" (click)="onClick()">
      <div class="mx-1 font-semibold">{{ processValue?.name }}</div>
      <div class="bg-white rounded py-0.5 px-3 whitespace-nowrap min-h-[1.75rem] relative w-full text-center border border-sky-300">
        {{ processValue | processValue }}

        <div *ngIf="hasCommands(processValue)"
             class="absolute -top-2 -right-0.5 !text-[0] bg-sky-200 rounded-full border-sky-300 border-b rotate-45">
          <div class="codicon-wand codicon !text-[0.6rem] p-[2.5px]  -rotate-45"></div>
        </div>
      </div>
    </div>
  `
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
