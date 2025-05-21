import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, EventEmitter, input, Output } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { ProcessValue, TagDirection } from '../../api';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ProcessValueComponent, PvAndPosition } from './process-value.component';
import { TagDirectionPipe } from './tag-direction.pipe';

@Component({
  selector: 'app-process-values-categorized',
  imports: [CommonModule, ProcessValueComponent, PushPipe, TagDirectionPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (allProcessValues | ngrxPush) {
      <div class="flex flex-col gap-4 -mt-1">
        @for (direction of tagDirections; track direction) {
          <div>
            <span class="font-bold text-lg">{{ direction | tagDirection }}:</span>
            <div class="flex gap-2 items-start flex-wrap mt-1">
              @for (processValue of getProcessValuesOfCategory(direction); track processValue.name) {
                <app-process-value [processValue]="processValue"
                                   (openCommands)="openCommands.emit($event)"></app-process-value>
              } @empty {
                No process values for this category
              }
            </div>
          </div>
        }
      </div>
    } @else {
      <div class="flex gap-2 items-start flex-wrap">
        @for (processValue of processValuesFilteringConditionals(); track processValue.name) {
          <app-process-value [processValue]="processValue"
                             (openCommands)="openCommands.emit($event)"></app-process-value>
        } @empty {
          <div class="m-auto">No process values available</div>
        }
      </div>
    }
  `,
})
export class ProcessValuesCategorizedComponent {
  processValues = input<ProcessValue[]>();
  processValuesFilteringConditionals = computed(() => this.processValues()?.filter(processValue => processValue.condition_holds ?? true));
  @Output() openCommands = new EventEmitter<PvAndPosition>();
  allProcessValues = this.store.select(DetailsSelectors.allProcessValues);
  protected readonly tagDirections: TagDirection[] = ['input', 'output', 'na', 'unspecified'];
  protected readonly Object = Object;

  constructor(private store: Store) {}

  protected getProcessValuesOfCategory(direction: string) {
    const processValues = this.processValuesFilteringConditionals()?.filter(processValue => processValue.direction === direction) ?? [];
    processValues.sort((a, b) => a.name.localeCompare(b.name));
    return processValues;
  }
}
