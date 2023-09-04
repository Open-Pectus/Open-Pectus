import { ChangeDetectionStrategy, Component, HostBinding, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { map } from 'rxjs';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';
import { YAxisOverrideDialogData } from './process-plot-d3.types';

@Component({
  selector: 'app-yaxis-override-dialog',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="bg-white p-2.5 rounded-md border-2 flex flex-col absolute gap-2.5 shadow-md shadow-gray-400"
         [style.border-color]="axisConfiguration?.color"
         [style.transform]="data?.axisIndex !== 0 ? 'translateX(-100%)' : null" *ngrxLet="axisConfiguration; let axisConfiguration">
      <p class="whitespace-nowrap">Override y limits for <span [style.color]="axisConfiguration?.color">{{axisConfiguration?.label}}</span></p>
      <label class="flex justify-between">
        Max: <input min="0" type="number" class="border-b border-gray-500 w-32 text-right" [valueAsNumber]="axisConfiguration?.y_max">
      </label>
      <label class="flex justify-between">
        Min: <input min="0" type="number" class="border-b border-gray-500 w-32 text-right" [valueAsNumber]="axisConfiguration?.y_min">
      </label>
      <button class="bg-green-400 rounded p-1" (click)="onClose()">Save</button>
    </div>
  `,
})
export class YAxisOverrideDialogComponent {
  @Input() data?: YAxisOverrideDialogData;
  axisConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration).pipe(map(plotConfiguration => {
    if(plotConfiguration === undefined || this.data === undefined) return;
    return plotConfiguration.sub_plots[this.data.subplotIndex].axes[this.data.axisIndex];
  }));

  constructor(private store: Store) {}

  @HostBinding('style.left.px') get left() { return this.data?.position?.x; }

  @HostBinding('style.top.px') get top() { return this.data?.position?.y; }

  onClose() {
    this.store.dispatch(ProcessPlotActions.yOverrideDialogClosed());
  }
}
