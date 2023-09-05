import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { concatLatestFrom } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { map, Observable } from 'rxjs';
import { PlotAxis } from '../../api';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';

@Component({
  selector: 'app-yaxis-override-dialog',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ng-container *ngrxLet="data; let data">
      <div *ngrxLet="axisConfiguration; let axisConfiguration"
           class="bg-white p-2.5 rounded-md border-2 flex flex-col absolute gap-2.5 shadow-md shadow-gray-400"
           [style.margin]="margin"
           [style.border-color]="axisConfiguration?.color"
           [style.transform]="data?.axisIndex !== 0 ? 'translateX(-100%)' : null"
           [style.left.px]="data?.position?.x"
           [style.top.px]="data?.position?.y">
        <p class="whitespace-nowrap">Override y limits for <span [style.color]="axisConfiguration?.color">{{axisConfiguration?.label}}</span>
        </p>
        <label class="flex justify-between">
          Max: <input min="0" type="number" class="border-b border-gray-500 w-32 text-right" [valueAsNumber]="axisConfiguration?.y_max">
        </label>
        <label class="flex justify-between">
          Min: <input min="0" type="number" class="border-b border-gray-500 w-32 text-right" [valueAsNumber]="axisConfiguration?.y_min">
        </label>
        <button class="bg-green-400 rounded p-1" (click)="onClose()">Save</button>
      </div>
    </ng-container>
  `,
})
export class YAxisOverrideDialogComponent {
  @Input() margin?: string;

  protected data = this.store.select(ProcessPlotSelectors.yAxisOverrideDialogData);
  private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration);
  protected axisConfiguration: Observable<PlotAxis | undefined> = this.data.pipe(
    concatLatestFrom(() => this.plotConfiguration),
    map(([data, plotConfiguration]) => {
      if(plotConfiguration === undefined || data === undefined) return;
      return plotConfiguration.sub_plots[data.subplotIndex].axes[data.axisIndex];
    }),
  );

  constructor(private store: Store) {}

  onClose() {
    this.store.dispatch(ProcessPlotActions.yOverrideDialogClosed());
  }
}
