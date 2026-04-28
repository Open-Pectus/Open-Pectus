import { ChangeDetectionStrategy, Component, inject, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';

@Component({
  selector: 'app-x-axis-override-dialog',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (data() !== undefined) {
      <div class="fixed left-0 top-0 right-0 bottom-0" (click)="onClose()">&nbsp;</div>
      <div
          class="bg-white p-2.5 rounded-md border-2 border-gray-400 flex flex-col absolute gap-2.5 shadow-md shadow-gray-400 -translate-y-full"
          [style.margin]="margin"
          [style.left.px]="data()?.position?.x"
          [style.top.px]="data()?.position?.y"
          (keyup.enter)="saveButton.click()"
          (keyup.escape)="onClose()">
        <p class="whitespace-nowrap">Choose process value for x axis</p>
        <select #select class="border border-gray-800 rounded outline-none cursor-pointer">
          @for (option of options(); track option) {
            <option [value]="option"
                    [selected]="xAxisProcessValueName() === option">{{ option }}
            </option>
          }
        </select>
        <button #saveButton class="bg-green-400 rounded p-1"
                (click)="onSave(select.value)">Save
        </button>
      </div>
    }
  `
})
export class XAxisOverrideDialogComponent {
  @Input() margin?: string;
  private store = inject(Store);
  protected data = this.store.selectSignal(ProcessPlotSelectors.xAxisOverrideDialogData);
  protected options = this.store.selectSignal(ProcessPlotSelectors.xAxisProcessValueCandidates);
  protected xAxisProcessValueName = this.store.selectSignal(ProcessPlotSelectors.xAxisProcessValueName);

  onClose() {
    this.store.dispatch(ProcessPlotActions.xOverrideDialogClosed());
  }

  onSave(processValueName: string) {
    this.store.dispatch(ProcessPlotActions.xOverrideDialogSaveClicked({processValueName}));
  }
}
