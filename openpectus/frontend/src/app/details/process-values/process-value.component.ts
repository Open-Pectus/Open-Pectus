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
  standalone: true,
  imports: [NgIf, ProcessValuePipe],
  template: `
    <div class="flex flex-col bg-sky-100 p-0.5 items-center gap-1 rounded select-none border border-sky-200"
         [class.cursor-pointer]="hasCommands(processValue)" (click)="onClick()">
      <div class="mx-1 font-semibold">{{ processValue?.name }}</div>
      <div class="bg-white rounded py-0.5 px-2 whitespace-nowrap min-h-[1.75rem] relative w-full text-center border border-sky-200">
        {{ processValue | processValue }}

        <div *ngIf="hasCommands(processValue)" [class.codicon-wand]="hasCommands(processValue)"
             class="absolute -top-2 -right-1 p-[2.5px] codicon !text-[0.6rem] bg-vscode-background-grey-hover rounded-full"></div>
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
