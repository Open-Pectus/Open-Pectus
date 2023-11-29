import { NgClass, NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild } from '@angular/core';
import { CollapsibleElementStorageService } from './collapsible-element-storage.service';

@Component({
  selector: 'app-collapsible-element',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [NgIf, NgClass],
  template: `
    <div class="flex flex-col bg-sky-700 py-1.5 lg:rounded-md lg:p-1.5 shadow-lg relative transition-[padding-bottom]" [class.pb-0]="collapsed">
      <div class="flex items-center flex-wrap text-gray-100 p-2 gap-3 cursor-pointer select-none" (click)="toggleCollapsed()">
        <div class="flex flex-1 items-center mr-1">
          <span class="codicon !text-2xl mr-2" *ngIf="codiconName !== undefined" [ngClass]="codiconName"
                [style.margin-bottom.px]="codiconName === 'codicon-graph-line' ? -1 : codiconName === 'codicon-dashboard' ? -1 : null"
                [style.--vscode-symbolIcon-keywordForeground]="'initial'"></span>
          <span class="text-2xl font-bold">{{name}}</span>
        </div>
        <div class="flex gap-4 items-center mr-10" *ngIf="!collapsed" (click)="$event.stopPropagation()">
          <ng-content select="[buttons]"></ng-content>
        </div>

        <div class="codicon !text-2xl !font-bold absolute right-3 lg:right-4" [class.codicon-chevron-right]="collapsed"
             [class.codicon-chevron-down]="!collapsed"
             (click)="$event.stopPropagation(); toggleCollapsed()"></div>
      </div>
      <div class="bg-white lg:rounded-sm mt-1.5 h-full" [class.transition-[height]]="!isDragging" #content
           [class.overflow-hidden]="!contentOverflow"
           [style.height.px]="height" (transitionend)="onTransitionEndContentContainer($event)">
        <ng-content select="[content]"></ng-content>
      </div>
      <div class="absolute bottom-0 left-0 w-full h-1.5" [class.-mb-8]="widenDragHandler"
           [style.height.rem]="widenDragHandler ? 4 : null"
           [class.cursor-ns-resize]="heightResizable"
           [draggable]="heightResizable"
           (dragstart)="onDragStartHandle($event)" (dragend)="onDragEndHandle()"
           (mousedown)="onMouseDownHandle()" (mouseup)="onMouseUpHandle()"
           (drag)="onDragHandle($event)" (dragover)="allowDragOver($event)"></div>

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
  @Input() contentOverflow = false;
  @Input() codiconName?: string;
  @Output() contentHeightChanged = new EventEmitter<number>();
  @Output() collapseStateChanged = new EventEmitter<boolean>();
  @ViewChild('content') contentElementRef?: ElementRef<HTMLDivElement>;
  protected collapsed = false;
  protected widenDragHandler = false;
  protected isDragging = false;
  private minHeight = 200;

  constructor(private collapsibleElementStorageService: CollapsibleElementStorageService) {}

  protected get height() {
    if(this.collapsed) return 0;
    return this.heightResizable ? this.contentHeight : undefined;
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

  allowDragOver(event: DragEvent) {
    event.preventDefault(); // to avoid "not allowed" cursor and extra 0 clientY drag event.
  }

  protected onDragHandle(event: DragEvent) {
    if(!this.heightResizable) return;
    const element = event.target as HTMLDivElement;
    const parentElement = element.parentElement as HTMLDivElement;
    const top = parentElement.offsetTop;
    const contentTop = this.contentElementRef?.nativeElement.offsetTop;
    if(top === undefined || contentTop === undefined) return;
    const height = event.pageY - top - contentTop - 3; // 3 is half the draghandler height when not widened;
    if(height < this.minHeight) return;
    this.height = height;
  }

  protected onDragStartHandle(event: DragEvent) {
    if(event.dataTransfer === null) return;
    event.dataTransfer.dropEffect = 'move';
    event.dataTransfer.setDragImage(new Image(), 0, 0);
    this.isDragging = true;
  }

  protected onDragEndHandle() {
    this.isDragging = false;
    this.widenDragHandler = false;
    this.collapsibleElementStorageService.saveHeight(this.name, this.contentHeight);
  }

  protected onMouseDownHandle() {
    this.widenDragHandler = true;
  }

  protected onMouseUpHandle() {
    this.widenDragHandler = false;
  }

  protected toggleCollapsed() {
    this.collapsed = !this.collapsed;
    this.collapsibleElementStorageService.saveCollapsedState(this.name, this.collapsed);
    this.collapseStateChanged.emit(this.collapsed);
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
