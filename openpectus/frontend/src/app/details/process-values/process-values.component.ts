import { NgFor, NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { ProcessValue, ProcessValueCommand } from '../../api';
import { CollapsibleElementComponent } from '../../shared/collapsible-element.component';
import { ToggleButtonComponent } from '../../shared/toggle-button.component';
import { UtilMethods } from '../../shared/util-methods';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ProcessValuesActions } from './ngrx/process-values.actions';
import { ProcessValueCommandsComponent } from './process-value-commands.component';
import { ProcessValueComponent, PvAndPosition } from './process-value.component';

@Component({
  selector: 'app-process-values',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    CollapsibleElementComponent,
    NgIf,
    NgFor,
    ProcessValueComponent,
    ProcessValueCommandsComponent,
    PushPipe,
    ToggleButtonComponent,
  ],
  template: `
    <app-collapsible-element [name]="'Process Values'" (collapseStateChanged)="collapsed = $event" [codiconName]="'codicon-dashboard'">
      <app-toggle-button [label]="'All Process Values'" buttons [checked]="allProcessValues | ngrxPush"
                         (changed)="onToggleAllProcessValues($event)"></app-toggle-button>

      <div class="flex gap-2 py-2 px-1 lg:px-2 items-start flex-wrap" content *ngIf="!collapsed">
        <div class="m-auto" *ngIf="(processValues | ngrxPush)?.length === 0">No process values available</div>
        <app-process-value *ngFor="let processValue of (processValues | ngrxPush); trackBy: trackBy"
                           [processValue]="processValue"
                           (openCommands)="onOpenCommands($event)"></app-process-value>
      </div>
      <app-process-value-commands *ngIf="showCommands" popover class="absolute p-0 block overflow-visible"
                                  [processValueCommands]="pvAndPositionForPopover?.processValue?.commands"
                                  (shouldClose)="onCloseCommands($event)"
                                  [style.left.px]="pvAndPositionForPopover?.position?.x"
                                  [style.top.px]="pvAndPositionForPopover?.position?.y"></app-process-value-commands>
    </app-collapsible-element>
  `,
})
export class ProcessValuesComponent implements OnInit, OnDestroy {
  allProcessValues = this.store.select(DetailsSelectors.allProcessValues);
  processValues = this.store.select(DetailsSelectors.processValues);
  protected showCommands = false;
  protected pvAndPositionForPopover?: PvAndPosition;
  protected collapsed = false;

  constructor(private store: Store) {}

  trackBy(index: number, processValue: ProcessValue) {
    return processValue.name;
  }

  ngOnInit() {
    this.store.dispatch(ProcessValuesActions.processValuesComponentInitialized());
  }

  ngOnDestroy() {
    this.store.dispatch(ProcessValuesActions.processValuesComponentDestroyed());
  }

  onToggleAllProcessValues(checked: boolean) {
    this.store.dispatch(DetailsActions.toggleAllProcessValues({allProcessValues: checked}));
  }

  onCloseCommands(command?: ProcessValueCommand) {
    this.showCommands = false;
    if(command === undefined || this.pvAndPositionForPopover === undefined) return;
    this.store.dispatch(ProcessValuesActions.processValueCommandClicked(
      {processValueName: this.pvAndPositionForPopover.processValue.name, command: command},
    ));
  }

  onOpenCommands(pvAndPosition: PvAndPosition) {
    if(UtilMethods.isMobile) pvAndPosition.position.x = window.innerWidth / 2;
    this.pvAndPositionForPopover = pvAndPosition;
    this.showCommands = true;
  }
}
