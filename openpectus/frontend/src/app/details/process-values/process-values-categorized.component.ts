import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { ProcessValue, TagDirection } from '../../api';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ProcessValueComponent, PvAndPosition } from './process-value.component';

@Component({
  selector: 'app-process-values-categorized',
  standalone: true,
  imports: [CommonModule, ProcessValueComponent, PushPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex gap-2 items-start flex-wrap" *ngIf="!(allProcessValues | ngrxPush)">
      <div class="m-auto" *ngIf="(processValues | ngrxPush)?.length === 0">No process values available</div>
      <app-process-value *ngFor="let processValue of processValues; trackBy: trackBy"
                         [processValue]="processValue"
                         (openCommands)="openCommands.emit($event)"></app-process-value>
    </div>

    <div class="flex flex-col gap-4 -mt-1" *ngIf="allProcessValues | ngrxPush">
      <div *ngFor="let direction of Object.values(TagDirection)">
        <span class="font-bold text-lg">{{ direction | titlecase }}:</span>
        <div class="flex gap-2 items-start flex-wrap">
          <div class="" *ngIf="getProcessValuesOfCategory(direction).length === 0">No process values for this category</div>
          <app-process-value *ngFor="let processValue of getProcessValuesOfCategory(direction); trackBy: trackBy"
                             [processValue]="processValue"
                             (openCommands)="openCommands.emit($event)"></app-process-value>
        </div>
      </div>
    </div>
  `,
})
export class ProcessValuesCategorizedComponent {
  @Input() processValues?: ProcessValue[];
  @Output() openCommands = new EventEmitter<PvAndPosition>();
  allProcessValues = this.store.select(DetailsSelectors.allProcessValues);
  protected readonly TagDirection = TagDirection;
  protected readonly Object = Object;

  constructor(private store: Store) {}

  trackBy(_: number, processValue: ProcessValue) {
    return processValue.name;
  }

  protected getProcessValuesOfCategory(direction: string) {
    if(this.processValues === undefined) return [];
    const processValues = this.processValues.filter(processValue => processValue.direction === direction);
    processValues.sort((a, b) => b.name.localeCompare(a.name));
    return processValues;
  }
}
