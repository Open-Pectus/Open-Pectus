import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

@Component({
  selector: 'app-collapsible-element',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col bg-sky-700 p-1.5 rounded-md shadow-lg cursor-pointer" (click)="collapsed = !collapsed">
      <div class="flex justify-between items-center text-gray-100 m-2">
        <span class="text-2xl font-bold">{{name}}</span>
        <div class="codicon !text-2xl !font-bold" [class.codicon-chevron-right]="collapsed" [class.codicon-chevron-down]="!collapsed"></div>
      </div>
      <div class="bg-white rounded-sm overflow-hidden mt-1.5" *ngIf="!collapsed">
        <ng-content select="[content]"></ng-content>
      </div>
    </div>
  `,
})
export class CollapsibleElementComponent {
  @Input() name?: string;
  @Input() startCollapsed = false;
  collapsed = false;
}
