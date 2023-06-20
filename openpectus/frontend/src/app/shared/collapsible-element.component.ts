import { ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild } from '@angular/core';
import { CollapsibleElementStorageService } from './collapsible-element-storage.service';

@Component({
  selector: 'app-collapsible-element',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col bg-sky-700 p-1.5 rounded-md shadow-lg relative">
      <div class="flex justify-between items-center text-gray-100 p-2 cursor-pointer select-none" (click)="toggleCollapsed()">
        <span class="text-2xl font-bold">{{name}}</span>
        <div class="flex gap-4" (click)="$event.stopPropagation()">
          <ng-content select="button"></ng-content>
          <div class="codicon !text-2xl !font-bold" [class.codicon-chevron-right]="collapsed" [class.codicon-chevron-down]="!collapsed"
               (click)="toggleCollapsed()"></div>
        </div>
      </div>
      <div class="bg-white rounded-sm overflow-hidden mt-1.5 h-full" [class.transition-[height]]="!isDragging" #content
           [style.height.px]="height" (transitionend)="onTransitionEndContentContainer($event)">
        <ng-content select="[content]"></ng-content>
      </div>
      <div class="absolute bottom-0 left-0 w-full h-1.5" [style.height.px]="widenDragHandler ? 20 : null"
           [class.cursor-ns-resize]="heightResizable"
           [draggable]="heightResizable"
           (dragstart)="onDragStartHandle($event)" (dragend)="onDragEndHandle()"
           (mousedown)="onMouseDownHandle()" (mouseleave)="onMouseLeaveHandle()"
           (drag)="onDragHandle($event)"></div>

      <div class="absolute top-0 left-0">
        <ng-content select="[popover]"></ng-content>
      </div>
    </div>
  `,
})
export class CollapsibleElementComponent implements OnInit {
  @Input() name?: string;
  @Input() heightResizable = false;
  @Input() contentHeight = 0;
  @Output() contentHeightChanged = new EventEmitter<number>();
  @ViewChild('content') contentElementRef?: ElementRef<HTMLDivElement>;
  protected collapsed = false;
  protected widenDragHandler = false;
  protected isDragging = false;

  constructor(private collapsibleElementStorageService: CollapsibleElementStorageService) {}

  protected get height() {
    if(this.collapsed) return 0;
    return this.heightResizable ? this.contentHeight : this.contentElementRef?.nativeElement.scrollHeight;
  }

  private set height(height: number | undefined) {
    if(height === undefined) return;
    this.contentHeight = height;
    this.contentHeightChanged.emit(this.height);
  }

  ngOnInit() {
    this.getHeightFromStorage();
    this.getCollapsedStateFromStorage();
  }

  protected onDragHandle(event: DragEvent) {
    if(!this.heightResizable) return;
    const element = event.target as HTMLDivElement;
    const parentElement = element.parentElement as HTMLDivElement;
    const top = parentElement.offsetTop;
    const contentTop = this.contentElementRef?.nativeElement.offsetTop;
    if(top === undefined || contentTop === undefined) return;
    const height = event.pageY - top - contentTop;
    if(height < 100) return;
    this.height = height;
  }

  protected onDragStartHandle(event: DragEvent) {
    if(event.dataTransfer === null) return;
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.dropEffect = 'move';
    event.dataTransfer.setDragImage(new Image(), 0, 0);
    this.isDragging = true;
  }

  protected onDragEndHandle() {
    this.isDragging = false;
    this.collapsibleElementStorageService.saveHeight(this.name, this.contentHeight);
  }

  protected onMouseDownHandle() {
    this.widenDragHandler = true;
  }

  protected onMouseLeaveHandle() {
    this.widenDragHandler = false;
  }

  protected toggleCollapsed() {
    this.collapsed = !this.collapsed;
    this.collapsibleElementStorageService.saveCollapsedState(this.name, this.collapsed);
  }

  protected onTransitionEndContentContainer(event: TransitionEvent) {
    if(event.propertyName === 'height') this.contentHeightChanged.emit(this.height);
  }

  private getHeightFromStorage() {
    if(this.name === undefined) throw Error('Name of CollapsibleElementComponent should be defined');
    const height = this.collapsibleElementStorageService.getHeight(this.name);
    if(height === null) return;
    this.height = height;
  }

  private getCollapsedStateFromStorage() {
    if(this.name === undefined) throw Error('Name of CollapsibleElementComponent should be defined');
    const collapsed = this.collapsibleElementStorageService.getCollapsedState(this.name);
    if(collapsed === null) return;
    this.collapsed = collapsed;
  }
}
