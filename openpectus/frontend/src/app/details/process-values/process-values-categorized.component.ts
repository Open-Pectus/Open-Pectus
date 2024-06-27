import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, input, Output } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { ProcessValue } from '../../api/models/ProcessValue';
import { TagDirection } from '../../api/models/TagDirection';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ProcessValueComponent, PvAndPosition } from './process-value.component';
import { TagDirectionPipe } from './tag-direction.pipe';

@Component({
  selector: 'app-process-values-categorized',
  standalone: true,
  imports: [CommonModule, ProcessValueComponent, PushPipe, TagDirectionPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (allProcessValues | ngrxPush) {
      <div class="flex flex-col gap-4 -mt-1">
        @for (direction of Object.values(TagDirection); track direction) {
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
        @for (processValue of processValues(); track processValue.name) {
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
  @Output() openCommands = new EventEmitter<PvAndPosition>();
  allProcessValues = this.store.select(DetailsSelectors.allProcessValues);
  protected readonly TagDirection = TagDirection;
  protected readonly Object = Object;

  constructor(private store: Store) {}

  protected getProcessValuesOfCategory(direction: string) {
    const processValues = this.processValues()?.filter(processValue => processValue.direction === direction) ?? [];
    processValues.sort((a, b) => a.name.localeCompare(b.name));
    return processValues;
  }
}
