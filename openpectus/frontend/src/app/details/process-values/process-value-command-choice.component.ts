import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { ProcessValueCommand, ProcessValueCommandChoiceValue } from '../../api';

@Component({
  selector: 'app-process-value-command-choice',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex items-center">
      <p class="mr-2">{{command?.name}}: </p>
      <button *ngFor="let option of options" [attr.disabled]="command?.disabled" [class.!bg-gray-400]="command?.disabled"
              class="bg-green-400 text-gray-800 border-l border-white first-of-type:border-none first-of-type:rounded-l-md last-of-type:rounded-r-md py-2 px-3 whitespace-pre font-semibold focus:z-10"
              (click)="$event.stopPropagation(); choiceMade.emit(option)">{{option}}</button>
    </div>
  `,
})
export class ProcessValueCommandChoiceComponent {
  @Input() command?: ProcessValueCommand;
  @Output() choiceMade = new EventEmitter<string>();

  get options() {
    if(this.command?.value?.value_type !== ProcessValueCommandChoiceValue.value_type.CHOICE) return [];
    return this.command.value.options;
  }
}
