import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { InProgress, NotOnline, ProcessUnit, Ready } from '../../api';
import { UtilMethods } from '../../shared/util-methods';

@Component({
  selector: 'app-process-unit-card',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="rounded-md shadow-md cursor-pointer bg-vscode-background-grey hover:brightness-95">
      <div class="px-5 py-3 text-xl bg-vscode-mediumblue text-white rounded-t-md flex justify-between">
        <div>{{processUnit?.name}}</div>
        <div class="ml-2 codicon !text-xl" [ngClass]="statusIcon"></div>
      </div>
      <div class="px-5 py-4 ">
        <div>State: {{processUnit?.state?.state | processUnitState}}</div>
        <div>Location: {{processUnit?.location}}</div>
        <div>Runtime: {{processUnit?.runtime_msec | formatDurationMsec}}</div>
      </div>
    </div>
  `,
})
export class ProcessUnitCardComponent {
  @Input() processUnit?: ProcessUnit;

  get statusIcon() {
    const state = this.processUnit?.state.state;
    switch(state) {
      case undefined:
        return '';
      case InProgress.state.IN_PROGRESS:
        return 'codicon-play-circle';
      case Ready.state.READY:
        return 'codicon-pass';
      case NotOnline.state.NOT_ONLINE:
        return 'codicon-circle-slash';
      default:
        return UtilMethods.assertNever(state);
    }
  }
}
