import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { RunLogLine } from '../../api';

@Component({
  selector: 'app-run-log-line',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="">
      {{runLogLine?.start | date}}
      {{runLogLine?.end | date}}
      {{runLogLine?.command?.command}}
    </div>
  `,
})
export class RunLogLineComponent {
  @Input() runLogLine?: RunLogLine;


}
