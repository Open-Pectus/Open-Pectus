import { ChangeDetectionStrategy, Component, ElementRef, Input, ViewChild } from '@angular/core';
import { RunLogColumn, RunLogLine } from '../../api';

@Component({
  selector: 'app-run-log-line',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div [class.!bg-gray-200]="rowIndex % 2 === 1" class="bg-gray-100 border-b border-white cursor-pointer" (click)="toggleCollapse()">
      <div class="grid gap-2 px-3 py-2" [style.grid]="gridFormat">
        <p>{{runLogLine?.start | date:dateFormat}}</p>
        <p *ngIf="runLogLine?.end !== undefined">{{runLogLine?.end | date:dateFormat}}</p>
        <progress [value]="runLogLine?.progress" class="h-full w-28" [style.border-width]="'revert'" [style.border-style]="'revert'"
                  [style.border-color]="'revert'" *ngIf="runLogLine?.end === undefined"></progress>
        <p>{{runLogLine?.command?.command}}</p>
      </div>
      <div [style.height.px]="height" class="w-full transition-[height] overflow-hidden">
        <div #additionalValues class="grid grid-rows-1 px-2 grid-flow-col justify-end">
          <div *ngFor="let additionalValue of runLogLine?.additional_values; let valueIndex = index"
               class="mx-2 mb-2 border border-sky-700 rounded-md text-right overflow-hidden">
            <p class="bg-sky-700 text-white px-2 py-0.5">{{additionalColumns?.[valueIndex]?.header}}</p>
            <p class="px-2 py-0.5 bg-white ">{{additionalValue | processValue:additionalColumns?.[valueIndex]?.type:additionalColumns?.[valueIndex]?.unit}}</p>
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
