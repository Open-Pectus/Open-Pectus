import { ChangeDetectionStrategy, Component, ElementRef, Input, ViewChild } from '@angular/core';
import { RunLogColumn, RunLogLine } from '../../api';

@Component({
  selector: 'app-run-log-line',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div [class.!bg-slate-100]="rowIndex % 2 === 1" class="bg-white border-b border-white cursor-pointer" (click)="toggleCollapse()">
      <div class="grid gap-2 px-3 py-2" [style.grid]="gridFormat">
        <p>{{runLogLine?.start | date:dateFormat}}</p>
        <p>{{runLogLine?.end | date:dateFormat}}</p>
        <p>{{runLogLine?.command?.command}}</p>
      </div>
      <div [style.height.px]="height" class="w-full transition-[height] overflow-hidden">
        <div #additionalValues class="grid grid-rows-1 px-2 grid-flow-col justify-end">
          <div *ngFor="let additionalValue of runLogLine?.additional_values; let valueIndex = index"
               class="m-2 p-2 border border-slate-300 rounded-md text-right">
            <p class="font-semibold">{{additionalColumns?.[valueIndex]?.header}}</p>
            <p>{{additionalValue | processValue:additionalColumns?.[valueIndex]?.type:additionalColumns?.[valueIndex]?.unit}}</p>
          </div>
        </div>
      </div>
    </div>
  `,
})
export class RunLogLineComponent {
  @Input() runLogLine?: RunLogLine;
  @Input() rowIndex: number = 0;
  @Input() additionalColumns?: RunLogColumn[];
  @Input() gridFormat?: string = 'auto / 1fr 1fr 1fr';
  @ViewChild('additionalValues', {static: true}) additionalValuesElement!: ElementRef<HTMLDivElement>;
  dateFormat = 'dd/MM HH:mm:ss';
  protected collapsed = true;

  get height() {
    return this.collapsed ? 0 : this.additionalValuesElement.nativeElement.scrollHeight;
  }

  toggleCollapse() {
    this.collapsed = !this.collapsed;
  }
}
