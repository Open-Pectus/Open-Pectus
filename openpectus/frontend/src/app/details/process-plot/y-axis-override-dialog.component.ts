import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, ElementRef, Input, ViewChild } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { map, Observable, tap } from 'rxjs';
import { PlotAxis } from '../../api/models/PlotAxis';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { AxisLimits } from './process-plot.types';

@Component({
  selector: 'app-y-axis-override-dialog',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [LetDirective, NgIf],
  template: `
    <ng-container *ngrxLet="data; let data">
      <ng-container *ngIf="data !== undefined">
        <div class="fixed left-0 top-0 right-0 bottom-0" (click)="onClose()"></div>
        <div *ngrxLet="axisConfiguration; let axisConfiguration"
             class="bg-white p-2.5 rounded-md border-2 flex flex-col absolute gap-2.5 shadow-md shadow-gray-400"
             [style.margin]="margin"
             [style.border-color]="axisConfiguration?.color"
             [style.transform]="data?.axisIndex !== 0 ? 'translateX(-100%)' : null"
             [style.left.px]="data?.position?.x"
             [style.top.px]="data?.position?.y"
             (keyup.enter)="saveButton.click()"
             (keyup.escape)="onClose()">
          <p class="whitespace-nowrap">
            Override y limits for <span [style.color]="axisConfiguration?.color">{{ axisConfiguration?.label }}</span>
          </p>
          <label class="flex justify-between">
            Max: <input #max min="0" type="number" class="border-b border-gray-500 w-32 text-right" [valueAsNumber]="axisConfiguration?.y_max">
          </label>
          <label class="flex justify-between">
            Min: <input #min min="0" type="number" class="border-b border-gray-500 w-32 text-right" [valueAsNumber]="axisConfiguration?.y_min">
          </label>
          <button #saveButton class="bg-green-400 rounded p-1"
                  (click)="onSave(data?.subplotIndex, data?.axisIndex, {min: min.valueAsNumber, max: max.valueAsNumber})">Save
          </button>
        </div>
      </ng-container>
    </ng-container>
  `,
})
export class YAxisOverrideDialogComponent {
  @Input() margin?: string;
  @ViewChild('max') maxInput?: ElementRef<HTMLInputElement>;
  protected data = this.store.select(ProcessPlotSelectors.yAxisOverrideDialogData);
  private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration);
  private yAxesLimitsOverride = this.store.select(ProcessPlotSelectors.yAxesLimitsOverride);
  protected axisConfiguration: Observable<PlotAxis | undefined> = this.data.pipe(
    concatLatestFrom(() => [
      this.plotConfiguration,
      this.yAxesLimitsOverride,
    ]),
    map(([data, plotConfiguration, yAxesLimitsOverride]) => {
      if(plotConfiguration === undefined || data === undefined) return;
      const yAxisOverride = yAxesLimitsOverride?.[data.subplotIndex]?.[data.axisIndex];
      const axisConfig = plotConfiguration.sub_plots[data.subplotIndex].axes[data.axisIndex];
      return {
        ...axisConfig,
        y_min: yAxisOverride?.min ?? axisConfig.y_min,
        y_max: yAxisOverride?.max ?? axisConfig.y_max,
      };
    }),
    tap(axisConfiguration => {
      if(axisConfiguration !== undefined) setTimeout(() => this.maxInput?.nativeElement.select());
    }),
  );

  constructor(private store: Store) {}

  onClose() {
    this.store.dispatch(ProcessPlotActions.yOverrideDialogClosed());
  }

  onSave(subplotIndex: number | undefined, axisIndex: number | undefined, limits: AxisLimits) {
    if(subplotIndex === undefined || axisIndex === undefined) return;
    this.store.dispatch(ProcessPlotActions.yOverrideDialogSaveClicked({subplotIndex, axisIndex, limits}));
  }
}
