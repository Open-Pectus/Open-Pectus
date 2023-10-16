import { AfterViewInit, ChangeDetectionStrategy, ChangeDetectorRef, Component, EventEmitter, Input, Output } from '@angular/core';
import { Store } from '@ngrx/store';
import { map } from 'rxjs';
import { RunLogLine } from '../../api';
import { RunLogActions } from './ngrx/run-log.actions';
import { RunLogSelectors } from './ngrx/run-log.selectors';
import { AdditionalValueType } from './run-log-additional-values.component';

@Component({
  selector: 'app-run-log-line',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div [class.!bg-gray-200]="rowIndex % 2 === 1" class="bg-gray-100 border-b border-white cursor-pointer"
         *ngrxLet="expanded as expanded" (click)="toggleCollapse(expanded)">
      <div class="grid gap-2 px-3 py-2" [style.grid]="gridFormat">
        <p>{{runLogLine?.start ?? '' | date}}</p>
        <p *ngIf="runLogLine?.end !== undefined">{{runLogLine?.end ?? '' | date}}</p>
        <progress [attr.value]="runLogLine?.progress" class="h-full w-28" [style.border-width]="'revert'" [style.border-style]="'revert'"
                  [style.border-color]="'revert'" *ngIf="runLogLine?.end === undefined"></progress>
        <p>{{runLogLine?.command?.command}}</p>
      </div>
      <div [style.height.px]="expanded && additionalValuesElementHasHeight ? additionalValues.scrollHeight : 0"
           [class.transition-[height]]="initialHeightAchieved"
           class="w-full overflow-hidden">
        <div #additionalValues>
          <p class="text-end p-2" *ngIf="!runLogLine?.start_values?.length && !runLogLine?.end_values?.length">
            No additional values available.
          </p>
          <app-run-log-additional-values *ngIf="runLogLine?.start_values?.length" [type]="AdditionalValueType.Start"
                                         [values]="runLogLine?.start_values"></app-run-log-additional-values>
          <app-run-log-additional-values *ngIf="runLogLine?.end_values?.length" [type]="AdditionalValueType.End"
                                         [values]="runLogLine?.end_values"></app-run-log-additional-values>
        </div>
      </div>
    </div>
  `,
})
export class RunLogLineComponent implements AfterViewInit {
  @Input() runLogLine?: RunLogLine;
  @Input() rowIndex: number = 0;
  @Input() gridFormat?: string = 'auto / 1fr 1fr 1fr';
  @Output() collapseToggled = new EventEmitter<boolean>();
  protected readonly AdditionalValueType = AdditionalValueType;
  protected readonly expanded = this.store.select(RunLogSelectors.expandedLines).pipe(
    map(lineIds => lineIds.some(lineId => lineId === this.runLogLine?.id)),
  );
  protected additionalValuesElementHasHeight = false;
  protected initialHeightAchieved = false;

  constructor(private store: Store, private cd: ChangeDetectorRef) {}

  ngAfterViewInit() {
    setTimeout(() => {
      this.additionalValuesElementHasHeight = true;
      this.cd.markForCheck();
      setTimeout(() => {
        this.initialHeightAchieved = true;
        this.cd.markForCheck();
      });
    });
  }

  protected toggleCollapse(expanded: boolean) {
    if(this.runLogLine === undefined) return;
    this.store.dispatch(expanded
                        ? RunLogActions.collapseLine({id: this.runLogLine.id})
                        : RunLogActions.expandLine({id: this.runLogLine.id}));
  }
}
