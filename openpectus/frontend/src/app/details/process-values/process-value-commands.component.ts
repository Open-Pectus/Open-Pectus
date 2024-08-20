import { NgFor, NgIf } from '@angular/common';
import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  Output,
  QueryList,
  ViewChild,
  ViewChildren,
} from '@angular/core';
import { produce } from 'immer';
import { ProcessValueCommand } from '../../api/models/ProcessValueCommand';
import { ProcessValueCommandChoiceValue } from '../../api/models/ProcessValueCommandChoiceValue';
import { ProcessValueType } from '../../api/models/ProcessValueType';
import { ProcessValueCommandButtonComponent } from './process-value-command-button.component';
import { ProcessValueCommandChoiceComponent } from './process-value-command-choice.component';
import { ProcessValueEditorComponent, ValueAndUnit } from './process-value-editor.component';

type FocusableCommandComponent = ProcessValueCommandButtonComponent | ProcessValueEditorComponent | ProcessValueCommandChoiceComponent;

@Component({
  selector: 'app-process-value-commands',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    NgFor,
    NgIf,
    ProcessValueEditorComponent,
    ProcessValueCommandChoiceComponent,
    ProcessValueCommandButtonComponent,
  ],
  template: `
    <div tabindex="0" #container
         class="absolute left-1/2 -translate-x-1/2 top-0.5 z-10 flex flex-col gap-3 p-3 bg-white border-4 border-sky-50 outline outline-1 outline-slate-500 rounded-md shadow-lg shadow-slate-500"
         (blur)="onBlur($event)">

      <ng-container *ngFor="let command of processValueCommands">
        <app-process-value-editor #focusableElement *ngIf="shouldUseEditor(command)" [command]="command" (inputBlur)="onBlur($event)"
                                  (save)="onEditorSave($event, command)"></app-process-value-editor>
        <app-process-value-command-choice #focusableElement [command]="command" *ngIf="shouldUseChoice(command)" (buttonBlur)="onBlur($event)"
                                          (choiceMade)="onChoiceMade($event, command)"></app-process-value-command-choice>
        <app-process-value-command-button #focusableElement [command]="command" *ngIf="shouldUseButton(command)" (buttonBlur)="onBlur($event)"
                                          (click)="$event.stopPropagation(); onButtonClick(command)"></app-process-value-command-button>
      </ng-container>
    </div>
  `,
})
export class ProcessValueCommandsComponent implements AfterViewInit {
  @Output() shouldClose = new EventEmitter<ProcessValueCommand | undefined>();
  @Input() processValueCommands?: ProcessValueCommand[];
  @ViewChild('container', {static: true}) container!: ElementRef<HTMLDivElement>;
  @ViewChildren('focusableElement') focusableElements!: QueryList<FocusableCommandComponent>;

  ngAfterViewInit() {
    this.focusableElements.first?.focus();
  }

  onBlur(event: FocusEvent) {
    // only close if it is not one of our subelements buttons or editors receiving focus.
    if((event.relatedTarget as Element | null)?.compareDocumentPosition(this.container.nativeElement) === 10) return;
    this.shouldClose.emit();
  }

  onButtonClick(command: ProcessValueCommand) {
    this.shouldClose.emit(command);
  }

  onEditorSave(valueAndUnit: ValueAndUnit | undefined, command: ProcessValueCommand) {
    if(valueAndUnit === undefined) return this.shouldClose.emit(command);
    const editedCommand = produce(command, draft => {
      if(draft.value === undefined) return;
      if(draft.value.value_type === ProcessValueType.INT || draft.value.value_type === ProcessValueType.FLOAT) {
        draft.value.value = parseFloat(valueAndUnit.value.replace(',', '.'));
        draft.value.value_unit = valueAndUnit.unit;
      } else {
        draft.value.value = valueAndUnit.value;
      }
    });
    this.shouldClose.emit(editedCommand);
  }

  shouldUseEditor(command: ProcessValueCommand) {
    return command.value?.value_type !== undefined && command.value?.value_type !== ProcessValueCommandChoiceValue.value_type.CHOICE;
  }

  shouldUseChoice(command: ProcessValueCommand) {
    return command.value?.value_type === ProcessValueCommandChoiceValue.value_type.CHOICE;
  }

  shouldUseButton(command: ProcessValueCommand) {
    return command?.value === undefined;
  }

  onChoiceMade(optionChosen: string, command: ProcessValueCommand) {
    const editedCommand = produce(command, draft => {
      if(draft.value === undefined) return;
      draft.value.value = optionChosen;
    });
    this.shouldClose.emit(editedCommand);
  }
}
