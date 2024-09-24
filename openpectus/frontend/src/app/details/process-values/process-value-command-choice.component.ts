import { NgFor } from '@angular/common';
import { ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { ProcessValueCommand } from '../../api';

@Component({
  selector: 'app-process-value-command-choice',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [NgFor],
  template: `
    <div class="flex items-center">
      <p class="mr-2">{{ command?.name }}: </p>
      <button #button *ngFor="let option of options" [attr.disabled]="command?.disabled" [class.!bg-gray-400]="command?.disabled"
              class="bg-green-400 text-gray-800 border-l border-white first-of-type:border-none first-of-type:rounded-l-md last-of-type:rounded-r-md py-2 px-3 whitespace-pre font-semibold focus:z-10"
              (click)="$event.stopPropagation(); choiceMade.emit(option)" (blur)="buttonBlur.emit($event)">{{ option }}
      </button>
    </div>
  `,
})
export class ProcessValueCommandChoiceComponent {
  @Input() command?: ProcessValueCommand;
  @Output() choiceMade = new EventEmitter<string>();
  @Output() buttonBlur = new EventEmitter<FocusEvent>();
  @ViewChild('button') button!: ElementRef<HTMLButtonElement>;

  get options() {
    if(this.command?.value?.value_type !== 'choice') return [];
    return this.command.value.options;
  }

  focus() {
    this.button.nativeElement.focus();
  }
}
