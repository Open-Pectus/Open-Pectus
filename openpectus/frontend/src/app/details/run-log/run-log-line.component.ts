import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { RunLogColumn, RunLogLine } from '../../api';

@Component({
  selector: 'app-run-log-line',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="grid grid-cols-3 gap-2 px-3 py-2" [style.grid]="gridFormat" [class.bg-slate-100]="index % 2 === 1">
      <p>{{runLogLine?.start | date}}</p>
      <p>{{runLogLine?.end | date}}</p>
      <p>{{runLogLine?.command?.command}}</p>
      <p *ngFor="let additionalValue of runLogLine?.additional_values; let index = index">
        {{additionalValue | processValuePipe:additionalColumns?.[index]?.type:additionalColumns?.[index]?.unit}}
      </p>
    </div>
  `,
})
export class RunLogLineComponent {
  @Input() runLogLine?: RunLogLine;
  @Input() index: number = 0;
  @Input() additionalColumns?: RunLogColumn[];
  @Input() gridFormat: string = 'auto / 1fr 1fr 1fr';

}
