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
    <div class="flex bg-vscode-background-grey-hover p-2 items-center gap-2 rounded select-none"
         [class.cursor-pointer]="hasAction(processValue)" (click)="onClick()">
      <div class="mx-1 font-semibold">{{processValue?.name}}</div>
      <div class="bg-white rounded py-0.5 px-2 whitespace-nowrap min-h-[1.75rem] relative">
        {{processValue | processValue}}

        <div *ngIf="hasAction(processValue)"
             [class.codicon-edit]="processValue?.writable" [class.codicon-wand]="hasCommands(processValue)"
             class="absolute -top-2 -right-2 p-[2.5px] codicon !text-[0.6rem] bg-vscode-background-grey-hover rounded-full"></div>
      </div>
    </div>
  `,
})
export class ProcessValueComponent {
  @Input() processValue?: ProcessValue;
  @Output() openEditor = new EventEmitter<PvAndPosition>();
  @Output() openCommands = new EventEmitter<PvAndPosition>();

  constructor(private element: ElementRef<HTMLDivElement>) {}

  onClick() {
    if(this.processValue === undefined) return;
    const domElement = this.element.nativeElement;
    const position = {x: domElement.offsetLeft + domElement.offsetWidth / 2, y: domElement.offsetTop + domElement.offsetHeight};
    const emitValue = {processValue: this.processValue, position};
    if(this.processValue.writable) this.openEditor.emit(emitValue);
    if(this.processValue.commands !== undefined && this.processValue.commands.length > 0) this.openCommands.emit(emitValue);
  }

  hasCommands(processValue?: ProcessValue) {
    return processValue?.commands !== undefined && processValue?.commands?.length !== 0;
  }

  hasAction(processValue?: ProcessValue) {
    return processValue?.writable || this.hasCommands(processValue);
  }
}
