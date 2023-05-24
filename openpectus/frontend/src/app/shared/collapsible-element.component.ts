import { ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';

@Component({
  selector: 'app-collapsible-element',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col bg-sky-700 p-1.5 rounded-md shadow-lg relative">
      <div class="flex justify-between items-center text-gray-100 m-2 cursor-pointer" (click)="collapsed = !collapsed">
        <span class="text-2xl font-bold">{{name}}</span>
        <div class="flex gap-4" (click)="$event.stopPropagation()">
          <ng-content select="button"></ng-content>
          <div class="codicon !text-2xl !font-bold" [class.codicon-chevron-right]="collapsed" [class.codicon-chevron-down]="!collapsed"
               (click)="collapsed = !collapsed"></div>
        </div>
      </div>
      <div class="bg-white rounded-sm mt-1.5 h-full" #content *ngIf="!collapsed">
        <ng-content select="[content]"></ng-content>
      </div>
      <div class="absolute bottom-0 left-0 w-full h-1.5" [class.cursor-ns-resize]="resizableHeight" [draggable]="resizableHeight"
           (dragstart)="onDragStart($event)"
           (drag)="resizeHeight($event)" (dragleave)="resizeHeight($event)"></div>
    </div>
  `,
})
export class CollapsibleElementComponent {
  @Input() name?: string;
  @Input() collapsed = false;
  @Input() resizableHeight = false;
  @Output() contentHeightChanged = new EventEmitter<number>();
  @ViewChild('content') contentElementRef?: ElementRef<HTMLDivElement>;

  resizeHeight(event: DragEvent) {
    if(!this.resizableHeight) return;
    const element = event.target as HTMLDivElement;
    const parentElement = element.parentElement as HTMLDivElement;
    const contentTop = this.contentElementRef?.nativeElement.offsetTop;
    if(contentTop === undefined) return;
    const top = parentElement.offsetTop;
    if(top === undefined) return;
    const height = event.pageY - top - contentTop;
    if(height < 100) return;
    this.contentHeightChanged.emit(height);
  }

  onDragStart(event: DragEvent) {
    if(event.dataTransfer === null) return;
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.dropEffect = 'move';
    event.dataTransfer.setDragImage(new Image(), 0, 0);
  }
}
