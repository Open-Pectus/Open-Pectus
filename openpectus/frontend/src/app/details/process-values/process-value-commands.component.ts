import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { ProcessValueCommand } from '../../api';

@Component({
  selector: 'app-process-value-commands',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div tabindex="0" #element
         class="absolute left-1/2 -translate-x-1/2 top-8 z-10 flex gap-2 bg-white border border-slate-500 outline-none rounded-md p-2"
         (blur)="onBlur($event)">
      <button class="bg-sky-500 rounded-lg p-2" *ngFor="let command of processValueCommands"
              (click)="onButtonClick(command)">{{command.name}}</button>
    </div>
  `,
})
export class ProcessValueCommandsComponent implements AfterViewInit {
  @Output() shouldClose = new EventEmitter<ProcessValueCommand | undefined>();
  @Input() processValueCommands?: ProcessValueCommand[];
  @ViewChild('element', {static: true}) element?: ElementRef<HTMLDivElement>;

  ngAfterViewInit() {
    this.element?.nativeElement.focus();
  }

  onBlur(event: FocusEvent) {
    // only close if it is not one of our subelements (buttons) receiving focus. Otherwise, we would close before the button is clicked.
    if((event.relatedTarget as Element | null)?.parentElement !== this.element?.nativeElement) this.shouldClose.emit();
  }

  onButtonClick(command: ProcessValueCommand) {
    this.shouldClose.emit(command);
  }
}
