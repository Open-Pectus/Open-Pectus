import { ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { ProcessValueCommand } from '../../api/models/ProcessValueCommand';

@Component({
  selector: 'app-process-value-command-button',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  template: `
    <button #button [attr.disabled]="command?.disabled" [class.!bg-gray-400]="command?.disabled"
            class="bg-green-400 text-gray-800 rounded-md py-2 px-3 whitespace-pre font-semibold"
            (blur)="buttonBlur.emit($event)">{{ command?.name }}
    </button>
  `,
})
export class ProcessValueCommandButtonComponent {
  @Input() command?: ProcessValueCommand;
  @Output() buttonBlur = new EventEmitter<FocusEvent>();
  @ViewChild('button') button!: ElementRef<HTMLButtonElement>;

  focus() {
    this.button.nativeElement.focus();
  }
}
