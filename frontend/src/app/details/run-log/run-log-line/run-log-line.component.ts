import { DatePipe } from '@angular/common';
import {
  AfterViewInit,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  computed,
  inject,
  input,
  output
} from '@angular/core';
import { Store } from '@ngrx/store';
import { RunLogLine } from '../../../api';
import { RunLogActions } from '../ngrx/run-log.actions';
import { RunLogSelectors } from '../ngrx/run-log.selectors';
import { AdditionalValueType, RunLogAdditionalValuesComponent } from '../run-log-additional-values.component';
import { RunLogLineCancelButtonComponent } from './run-log-line-cancel-button.component';
import { RunLogLineForceButtonComponent } from './run-log-line-force-button.component';
import { RunLogLineProgressComponent } from './run-log-line-progress.component';

@Component({
  selector: 'app-run-log-line',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    RunLogLineProgressComponent,
    RunLogLineForceButtonComponent,
    RunLogLineCancelButtonComponent,
    RunLogAdditionalValuesComponent,
    DatePipe
  ],
  template: `
    <div [class.bg-slate-50]="rowIndex() % 2 === 0"
         [class.bg-slate-100]="rowIndex() % 2 === 1"
         [class.!bg-yellow-100]="runLogLine()?.forced && !runLogLine()?.cancelled && !runLogLine()?.failed"
         [class.!bg-red-200]="runLogLine()?.cancelled && !runLogLine()?.failed"
         [class.!bg-red-600]="runLogLine()?.failed"
         class="border-b-2 border-white cursor-pointer"
         (click)="toggleCollapse(expanded())">
      <div class="grid gap-2 px-3 py-2" [style.grid]="gridFormat()">
        <p>{{ runLogLine()?.start ?? '' | date }}</p>
        @if (runLogLine()?.end !== undefined) {
          <p>{{ runLogLine()?.end ?? '' | date }}</p>
        }
        @if (runLogLine()?.end === undefined) {
          <app-run-log-line-progress [value]="runLogLine()?.progress" class="py-0.5"
           />
        }
        <p>{{ runLogLine()?.command?.command }}</p>
        <div class="col-end-6 flex gap-2">
          @if (runLogLine()?.forcible) {
            <app-run-log-line-force-button [lineId]="runLogLine()?.id"
                                           (click)="$event.stopPropagation()" />
          }
          @if (runLogLine()?.cancellable) {
            <app-run-log-line-cancel-button [lineId]="runLogLine()?.id"
                                            (click)="$event.stopPropagation()" />
          }
        </div>
      </div>

      <div [style.height.px]="expanded() && additionalValuesElementHasHeight ? additionalValues.scrollHeight : 0"
           [class.transition-[height]]="initialHeightAchieved"
           class="w-full overflow-hidden">
        <div #additionalValues>
          @if (!runLogLine()?.start_values?.length && !runLogLine()?.end_values?.length) {
            <p class="text-end p-2">
              No additional values available.
            </p>
          }
          @if (runLogLine()?.start_values?.length) {
            <app-run-log-additional-values [type]="AdditionalValueType.Start"
                                           [values]="runLogLine()?.start_values" />
          }
          @if (runLogLine()?.end_values?.length) {
            <app-run-log-additional-values [type]="AdditionalValueType.End"
                                           [values]="runLogLine()?.end_values" />
          }
        </div>
      </div>
    </div>
  `
})
export class RunLogLineComponent implements AfterViewInit {
  readonly runLogLine = input<RunLogLine>();
  readonly rowIndex = input(0);
  readonly gridFormat = input<string | undefined>('auto / 1fr 1fr 1fr');
  readonly collapseToggled = output<boolean>();
  protected readonly AdditionalValueType = AdditionalValueType;
  protected additionalValuesElementHasHeight = false;
  protected initialHeightAchieved = false;
  private store = inject(Store);
  protected readonly expanded = computed(() => {
    const lineIds = this.store.selectSignal(RunLogSelectors.expandedLines);
    return lineIds().some(lineId => lineId === this.runLogLine()?.id);
  });
  private cd = inject(ChangeDetectorRef);

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
    const runLogLine = this.runLogLine();
    if(runLogLine === undefined) return;
    this.store.dispatch(expanded
                        ? RunLogActions.collapseLine({id: runLogLine.id})
                        : RunLogActions.expandLine({id: runLogLine.id}));
  }
}
