import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ProcessUnit, ProcessUnitStateEnum } from '../../api';

@Component({
  selector: 'app-process-unit-card',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="m-6 rounded-md shadow-md cursor-pointer bg-vscode-backgroundgrey hover:brightness-95">
      <div class="px-5 py-3 text-xl bg-vscode-mediumblue text-white rounded-t-md flex justify-between">
        <div>{{processUnit?.name}}</div>
        <div class="codicon !text-xl" [class.codicon-play-circle]="processUnit?.state?.state === ProcessUnitStateEnum.InProgress"
             [class.codicon-pass]="processUnit?.state?.state === ProcessUnitStateEnum.Ready"
             [class.codicon-circle-slash]="processUnit?.state?.state === ProcessUnitStateEnum.NotOnline"
        ></div>
      </div>
      <div class="px-5 py-4 ">
        <div>State: {{processUnit?.state?.state}}</div>
        <div>Location: {{processUnit?.location}}</div>
        <div>Runtime: {{processUnit?.runtime_msec | formatDurationMsec}}</div>
      </div>


    </div>
  `,
})
export class ProcessUnitCardComponent {
  @Input() processUnit?: ProcessUnit;
  protected readonly ProcessUnitStateEnum = ProcessUnitStateEnum;
}
