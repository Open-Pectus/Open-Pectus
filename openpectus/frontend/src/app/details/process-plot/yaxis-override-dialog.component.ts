import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { YAxisOverrideDialogData } from './process-plot-d3.types';

@Component({
  selector: 'app-yaxis-override-dialog',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="bg-white p-2 rounded border-gray-400 border-2 flex flex-col absolute gap-2"
         [style.left.px]="data?.position?.x"
         [style.top.px]="data?.position?.y">
      <p>Something</p>
      <button class="bg-green-400" (click)="onClose()">Button</button>
    </div>
  `,
})
export class YAxisOverrideDialogComponent {
  @Input() data?: YAxisOverrideDialogData;

  constructor(private store: Store) {}

  onClose() {
    this.store.dispatch(ProcessPlotActions.yOverrideDialogClosed());
  }
}
