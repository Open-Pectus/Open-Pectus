import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

@Component({
  selector: 'app-collapsible-element',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col bg-sky-700 p-1.5 rounded-md shadow-lg">
      <div class="flex justify-between items-center text-gray-100 m-2 cursor-pointer" (click)="collapsed = !collapsed">
        <span class="text-2xl font-bold">{{name}}</span>
        <div class="flex gap-4" (click)="$event.stopPropagation()">
          <ng-content select="button"></ng-content>
          <div class="codicon !text-2xl !font-bold" [class.codicon-chevron-right]="collapsed" [class.codicon-chevron-down]="!collapsed"
               (click)="collapsed = !collapsed"></div>
        </div>
      </div>
      <div class="bg-white rounded-sm mt-1.5" *ngIf="!collapsed">
        <ng-content select="[content]"></ng-content>
      </div>
    </div>
  `,
})
export class CollapsibleElementComponent {
  @Input() name?: string;
  @Input() collapsed = false;
}
