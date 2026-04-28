import { ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Output, ViewChild, input } from '@angular/core';
import { ProcessValueCommand } from '../../api';

@Component({
  selector: 'app-process-value-command-choice',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [],
  template: `
    <div class="flex items-center">
      <p class="mr-2">{{ command()?.name }}: </p>
      @for (option of options; track option) {
        <button #button [attr.disabled]="command()?.disabled" [class.!bg-gray-400]="command()?.disabled"
                class="bg-green-400 text-gray-800 border-l border-white first-of-type:border-none first-of-type:rounded-l-md last-of-type:rounded-r-md py-2 px-3 whitespace-pre font-semibold focus:z-10"
                (click)="$event.stopPropagation(); choiceMade.emit(option)" (blur)="buttonBlur.emit($event)">{{ option }}
        </button>
      }
    </div>
  `
})
export class ProcessValueCommandChoiceComponent {
  readonly command = input<ProcessValueCommand>();
  @Output() choiceMade = new EventEmitter<string>();
  @Output() buttonBlur = new EventEmitter<FocusEvent>();
  @ViewChild('button') button!: ElementRef<HTMLButtonElement>;

  get options() {
    const command = this.command();
    if(command?.value?.value_type !== 'choice') return [];
    return command.value.options;
  }

  focus() {
    this.button.nativeElement.focus();
  }
}
