import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { produce } from 'immer';
import { ProcessValueCommand } from '../../api';
import { ValueAndUnit } from './process-value-editor.component';

@Component({
  selector: 'app-process-value-commands',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div tabindex="0" #element
         class="absolute left-1/2 -translate-x-1/2 top-0.5 z-10 flex flex-col gap-2 bg-white border border-slate-500 outline-none rounded-md p-2"
         (blur)="onBlur($event)">

      <ng-container *ngFor="let command of processValueCommands">
        <app-process-value-editor *ngIf="command.value !== undefined" class="" [command]="command" (inputBlur)="onBlur($event)"
                                  (save)="onEditorSave($event, command)"></app-process-value-editor>
        <button *ngIf="command.value === undefined" [attr.disabled]="command.disabled" [class.!bg-gray-400]="command.disabled"
                class="bg-green-400 text-gray-800 rounded-md py-2 px-3 whitespace-pre font-semibold"
                (click)="$event.stopPropagation(); onButtonClick(command)">{{command.name}}</button>
      </ng-container>
    </div>
  `,
})
export class ProcessValueCommandsComponent implements AfterViewInit {
  @Output() shouldClose = new EventEmitter<ProcessValueCommand | undefined>();
  @Input() processValueCommands?: ProcessValueCommand[];
  @ViewChild('element', {static: true}) element!: ElementRef<HTMLDivElement>;

  ngAfterViewInit() {
    this.element?.nativeElement.focus();
  }

  onBlur(event: FocusEvent) {
    // only close if it is not one of our subelements buttons or editors receiving focus.
    if((event.relatedTarget as Element | null)?.compareDocumentPosition(this.element.nativeElement) === 10) return;
    this.shouldClose.emit();
  }

  onButtonClick(command: ProcessValueCommand) {
    this.shouldClose.emit(command);
  }

  onEditorSave(valueAndUnit: ValueAndUnit | undefined, command: ProcessValueCommand) {
    if(valueAndUnit === undefined) return this.shouldClose.emit(command);
    const editedCommand = produce(command, draft => {
      if(draft.value === undefined) return;
      draft.value.value = valueAndUnit.value;
      draft.value.value_unit = valueAndUnit.unit;
    });
    this.shouldClose.emit(editedCommand);
  }
}
