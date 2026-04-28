import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, input, output, viewChild, viewChildren } from '@angular/core';
import { produce } from 'immer';
import { ProcessValueCommand } from '../../api';
import { ProcessValueCommandButtonComponent } from './process-value-command-button.component';
import { ProcessValueCommandChoiceComponent } from './process-value-command-choice.component';
import { ProcessValueEditorComponent, ValueAndUnit } from './process-value-editor.component';

type FocusableCommandComponent = ProcessValueCommandButtonComponent | ProcessValueEditorComponent | ProcessValueCommandChoiceComponent;

@Component({
  selector: 'app-process-value-commands',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    ProcessValueEditorComponent,
    ProcessValueCommandChoiceComponent,
    ProcessValueCommandButtonComponent
  ],
  template: `
    <div tabindex="0" #container
         class="absolute left-1/2 -translate-x-1/2 top-0.5 z-10 flex flex-col gap-3 p-3 bg-white border-4 border-sky-50 outline outline-1 outline-slate-500 rounded-md shadow-lg shadow-slate-500"
         (blur)="onBlur($event)">

      @for (command of processValueCommands(); track command) {
        @if (shouldUseEditor(command)) {
          <app-process-value-editor #focusableElement [command]="command" (inputBlur)="onBlur($event)"
                                    (save)="onEditorSave($event, command)"/>
        }
        @if (shouldUseChoice(command)) {
          <app-process-value-command-choice #focusableElement [command]="command" (buttonBlur)="onBlur($event)"
                                            (choiceMade)="onChoiceMade($event, command)"/>
        }
        @if (shouldUseButton(command)) {
          <app-process-value-command-button #focusableElement [command]="command" (buttonBlur)="onBlur($event)"
                                            (click)="$event.stopPropagation(); onButtonClick(command)"/>
        }
      }
    </div>
  `
})
export class ProcessValueCommandsComponent implements AfterViewInit {
  readonly shouldClose = output<ProcessValueCommand | undefined>();
  readonly processValueCommands = input<ProcessValueCommand[]>();
  readonly container = viewChild.required<ElementRef<HTMLDivElement>>('container');
  readonly focusableElements = viewChildren<FocusableCommandComponent>('focusableElement');

  ngAfterViewInit() {
    this.focusableElements().at(0)?.focus();
  }

  onBlur(event: FocusEvent) {
    // only close if it is not one of our subelements buttons or editors receiving focus.
    if((event.relatedTarget as Element | null)?.compareDocumentPosition(this.container().nativeElement) === 10) return;
    this.shouldClose.emit(undefined);
  }

  onButtonClick(command: ProcessValueCommand) {
    this.shouldClose.emit(command);
  }

  onEditorSave(valueAndUnit: ValueAndUnit | undefined, command: ProcessValueCommand) {
    if(valueAndUnit === undefined) return this.shouldClose.emit(command);
    const editedCommand = produce(command, draft => {
      if(draft.value === undefined) return;
      if(draft.value.value_type === 'int' || draft.value.value_type === 'float') {
        draft.value.value = parseFloat(valueAndUnit.value.replace(',', '.'));
        draft.value.value_unit = valueAndUnit.unit;
      } else {
        draft.value.value = valueAndUnit.value;
      }
    });
    this.shouldClose.emit(editedCommand);
  }

  shouldUseEditor(command: ProcessValueCommand) {
    return command.value?.value_type !== undefined && command.value?.value_type !== 'choice';
  }

  shouldUseChoice(command: ProcessValueCommand) {
    return command.value?.value_type === 'choice';
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
