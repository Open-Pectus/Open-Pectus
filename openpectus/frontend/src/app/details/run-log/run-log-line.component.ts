import { ChangeDetectionStrategy, ChangeDetectorRef, Component, EventEmitter, Input, Output } from '@angular/core';
import { RunLogLine } from '../../api';
import { AdditionalValueType } from './run-log-additional-values.component';

@Component({
  selector: 'app-run-log-line',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div [class.!bg-gray-200]="rowIndex % 2 === 1" class="bg-gray-100 border-b border-white cursor-pointer" (click)="toggleCollapse()">
      <div class="grid gap-2 px-3 py-2" [style.grid]="gridFormat">
        <p>{{runLogLine?.start | date:dateFormat}}</p>
        <p *ngIf="runLogLine?.end !== undefined">{{runLogLine?.end | date:dateFormat}}</p>
        <progress [attr.value]="runLogLine?.progress" class="h-full w-28" [style.border-width]="'revert'" [style.border-style]="'revert'"
                  [style.border-color]="'revert'" *ngIf="runLogLine?.end === undefined"></progress>
        <p>{{runLogLine?.command?.command}}</p>
      </div>
      <div [style.height.px]="collapsed ? 0 : additionalValues.scrollHeight" class="w-full transition-[height] overflow-hidden">
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
export class RunLogLineComponent {
  @Input() runLogLine?: RunLogLine;
  @Input() rowIndex: number = 0;
  @Input() gridFormat?: string = 'auto / 1fr 1fr 1fr';
  @Output() collapseToggled = new EventEmitter<boolean>();
  @Input() dateFormat = 'MM-dd HH:mm:ss';
  protected readonly AdditionalValueType = AdditionalValueType;

  constructor(private cd: ChangeDetectorRef) {}

  private _collapsed = true;

  get collapsed(): boolean {
    return this._collapsed;
  }

  set collapsed(value: boolean) {
    this._collapsed = value;
    this.cd.markForCheck();
  }

  protected toggleCollapse() {
    this.collapsed = !this.collapsed;
    this.collapseToggled.emit(this.collapsed);
  }
}
