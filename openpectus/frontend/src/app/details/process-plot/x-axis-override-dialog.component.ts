import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';

@Component({
  selector: 'app-x-axis-override-dialog',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ng-container *ngrxLet="data; let data">
      <ng-container *ngIf="data !== undefined">
        <div class="fixed left-0 top-0 right-0 bottom-0" (click)="onClose()"></div>
        <div class="bg-white p-2.5 rounded-md border-2 flex flex-col absolute gap-2.5 shadow-md shadow-gray-400 -translate-y-full"
             [style.margin]="margin"
             [style.left.px]="data?.position?.x"
             [style.top.px]="data?.position?.y"
             (keyup.enter)="saveButton.click()"
             (keyup.escape)="onClose()">
          <p class="whitespace-nowrap">Choose process value for x axis</p>
          <select #select>
            <option *ngFor="let option of options | ngrxPush" [value]="option"
                    [selected]="(xAxisProcessValueName | ngrxPush) === option">{{option}}</option>
          </select>
          <button #saveButton class="bg-green-400 rounded p-1"
                  (click)="onSave(select.value)">Save
          </button>
        </div>
      </ng-container>
    </ng-container>
  `,
})
export class XAxisOverrideDialogComponent {
  @Input() margin?: string;
  protected data = this.store.select(ProcessPlotSelectors.xAxisOverrideDialogData);
  protected options = this.store.select(ProcessPlotSelectors.xAxisProcessValueCandidates);
  protected xAxisProcessValueName = this.store.select(ProcessPlotSelectors.xAxisProcessValueName);

  constructor(private store: Store) {}

  onClose() {
    this.store.dispatch(ProcessPlotActions.xOverrideDialogClosed());
  }

  onSave(processValueName: string) {
    this.store.dispatch(ProcessPlotActions.xOverrideDialogSaveClicked({processValueName}));
  }
}
