import { NgFor, NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { CommandExample } from '../../api/models/CommandExample';

@Component({
  selector: 'app-command-examples-list',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    NgIf,
    NgFor,
    PushPipe,
  ],
  styles: [
    ':host ::ng-deep ::-webkit-scrollbar { display: none; }',
    ':host { position: relative }',
  ],
  template: `
    <div class="flex flex-col gap-1 w-56 overflow-y-auto h-full pl-2 py-2" [style.scrollbar-width]="'none'">
      <div *ngIf="(commandExamples | ngrxPush)?.length === 0" class="m-auto">No examples available</div>
      <button *ngFor="let commandExample of commandExamples | ngrxPush"
              class="rounded-l-lg p-2 bg-sky-50 select-none border border-r-0 border-gray-400"
              [class.text-gray-700]="commandExample !== chosenExample"
              [class.!bg-white]="commandExample === chosenExample"
              [class.z-10]="commandExample === chosenExample"
              (click)="exampleChosen.emit(commandExample)">
        {{ commandExample.name }}
      </button>
    </div>
    <div class="h-full absolute right-0 top-0 w-0.5 bg-gradient-to-r from-transparent to-slate-500"></div>
  `,
})
export class CommandExamplesListComponent {
  @Input() commandExamples?: CommandExample[];
  @Input() chosenExample?: CommandExample;
  @Output() exampleChosen = new EventEmitter<CommandExample>();
}
