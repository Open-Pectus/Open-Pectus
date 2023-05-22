import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { CommandExample } from '../../api';

@Component({
  selector: 'app-command-examples-list',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col gap-1 max-w-[16rem] overflow-y-auto h-full pl-2 py-2" [style.scrollbar-width]="'none'">
      <button *ngFor="let commandExample of commandExamples | ngrxPush"
              class="rounded-l-2xl p-2 bg-slate-200 select-none border border-r-0 border-slate-500"
              [class.!bg-white]="commandExample === chosenExample"
              [class.z-10]="commandExample === chosenExample"
              (click)="exampleChosen.emit(commandExample)">
        {{commandExample.name}}
      </button>
    </div>
    <div class="h-full absolute right-0 top-0 w-0.5 bg-gradient-to-r from-transparent to-slate-500"></div>
  `,
  styles: [
    '::-webkit-scrollbar { display: none; }',
    ':host { position: relative }',
  ],
})
export class CommandExamplesListComponent {
  @Input() commandExamples?: CommandExample[];
  @Input() chosenExample?: CommandExample;
  @Output() exampleChosen = new EventEmitter<CommandExample>();
}
