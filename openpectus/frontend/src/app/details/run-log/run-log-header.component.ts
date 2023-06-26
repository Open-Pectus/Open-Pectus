import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-run-log-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="grid bg-gray-700 text-white gap-2 px-3 py-2" [style.grid]="gridFormat">
      <b>Start</b>
      <b>End</b>
      <b>Command</b>
      <button class="bg-gray-500 rounded px-2 flex items-center" (click)="expandAll.emit()">
        <div class="codicon codicon-unfold mr-1"></div>
        Expand all
      </button>
      <button class="bg-gray-500 rounded px-2 flex items-center" (click)="collapseAll.emit()">
        <div class="codicon codicon-fold mr-1"></div>
        Collapse all
      </button>
    </div>
  `,
})
export class RunLogHeaderComponent {
  @Input() gridFormat: string = '';
  @Output() expandAll = new EventEmitter<void>();
  @Output() collapseAll = new EventEmitter<void>();
}