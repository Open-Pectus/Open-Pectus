import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { ProcessValue, ProcessValueCommand } from '../../api';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ValueAndUnit } from './process-value-editor.component';
import { PvAndPosition } from './process-value.component';

@Component({
  selector: 'app-process-values',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Values'">
      <div class="flex gap-2 p-2 items-start flex-wrap" content>
        <div class="m-auto" *ngIf="(processValues | ngrxPush)?.length === 0">No process values available</div>
        <app-process-value *ngFor="let processValue of (processValues | ngrxPush); trackBy: trackBy"
                           [processValue]="processValue" (openEditor)="onOpenEditor($event)"
                           (openCommands)="onOpenCommands($event)"></app-process-value>
      </div>

      <app-process-value-editor *ngIf="showEditor" popover class="absolute p-0 block overflow-visible top-10"
                                [processValue]="pvAndPositionForPopover?.processValue"
                                (shouldClose)="onCloseEditor($event)"
                                [style.left.px]="pvAndPositionForPopover?.position?.x"
                                [style.top.px]="pvAndPositionForPopover?.position?.y"></app-process-value-editor>
      <app-process-value-commands *ngIf="showCommands" popover class="absolute p-0 block overflow-visible"
                                  [processValueCommands]="pvAndPositionForPopover?.processValue?.commands"
                                  (shouldClose)="onCloseCommands($event)"
                                  [style.left.px]="pvAndPositionForPopover?.position?.x"
                                  [style.top.px]="pvAndPositionForPopover?.position?.y"></app-process-value-commands>

    </app-collapsible-element>
  `,
})
export class ProcessValuesComponent implements OnInit, OnDestroy {
  processValues = this.store.select(DetailsSelectors.processValues);
  protected showEditor = false;
  protected showCommands = false;
  protected pvAndPositionForPopover?: PvAndPosition;

  constructor(private store: Store) {}

  trackBy(index: number, processValue: ProcessValue) {
    return processValue.name;
  }

  ngOnInit() {
    this.store.dispatch(DetailsActions.processValuesInitialized());
  }

  ngOnDestroy() {
    this.store.dispatch(DetailsActions.processValuesDestroyed());
  }

  onCloseCommands(command?: ProcessValueCommand) {
    this.showCommands = false;
    if(command === undefined || this.pvAndPositionForPopover === undefined) return;
    this.store.dispatch(DetailsActions.processValueCommandClicked(
      {processValueName: this.pvAndPositionForPopover.processValue.name, command: command},
    ));
  }

  onCloseEditor(valueAndUnit?: ValueAndUnit) {
    this.showEditor = false;
    if(valueAndUnit === undefined || this.pvAndPositionForPopover === undefined) return;
    this.store.dispatch(DetailsActions.processValueEdited(
      {processValue: {...this.pvAndPositionForPopover.processValue, value: valueAndUnit.value, value_unit: valueAndUnit.unit}},
    ));
  }

  onOpenEditor(pvAndPosition: PvAndPosition) {
    this.pvAndPositionForPopover = pvAndPosition;
    this.showEditor = true;
  }

  onOpenCommands(pvAndPosition: PvAndPosition) {
    this.pvAndPositionForPopover = pvAndPosition;
    this.showCommands = true;
  }
}
