import { ChangeDetectionStrategy, Component, ElementRef, input, output, viewChild } from '@angular/core';
import { ProcessValueCommand } from 'src/app/api';

@Component({
  selector: 'app-process-value-command-button',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button #button [attr.disabled]="command()?.disabled" [class.!bg-gray-400]="command()?.disabled"
            class="bg-green-400 text-gray-800 rounded-md py-2 px-3 whitespace-pre font-semibold"
            (blur)="buttonBlur.emit($event)">{{ command()?.name }}
    </button>
  `,
})
export class ProcessValueCommandButtonComponent {
  readonly command = input<ProcessValueCommand>();
  readonly buttonBlur = output<FocusEvent>();
  readonly button = viewChild.required<ElementRef<HTMLButtonElement>>('button');

  focus() {
    this.button().nativeElement.focus();
  }
}
