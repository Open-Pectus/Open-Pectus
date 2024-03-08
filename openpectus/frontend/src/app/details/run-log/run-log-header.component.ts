import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-run-log-header',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  template: `
    <div class="grid bg-slate-100 text-gray-900 items-center gap-2 px-3 py-2" [style.grid]="gridFormat">
      <b>Start</b>
      <b>End</b>
      <b>Command</b>
      <button class="bg-slate-50 border-gray-300 border rounded px-2 ml-2 flex items-center py-0.5" (click)="expandAll.emit()">
        <i class="codicon codicon-unfold mr-1"></i>
        <span class="whitespace-pre">Expand all</span>
      </button>
      <button class="bg-slate-50 border-gray-300 border rounded px-2 ml-2 flex items-center py-0.5" (click)="collapseAll.emit()">
        <i class="codicon codicon-fold mr-1"></i>
        <span class="whitespace-pre">Collapse all</span>
      </button>
    </div>
  `,
})
export class RunLogHeaderComponent {
  @Input() gridFormat: string = '';
  @Output() expandAll = new EventEmitter<void>();
  @Output() collapseAll = new EventEmitter<void>();
}
