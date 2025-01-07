import { NgClass } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ProcessUnit } from '../../api';
import { FormatDurationMsecPipe } from '../../shared/pipes/format-duration-msec.pipe';
import { ProcessUnitStatePipe } from '../../shared/pipes/process-unit-state.pipe';
import { UtilMethods } from '../../shared/util-methods';

@Component({
    selector: 'app-process-unit-card',
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [
        NgClass,
        FormatDurationMsecPipe,
        ProcessUnitStatePipe,
    ],
    template: `
    <div class="rounded-md shadow-md cursor-pointer bg-stone-100 hover:brightness-95">
      <div [class]="'px-5 py-3 text-white rounded-t-md flex justify-between ' + backgroundColor">
        <div class="font-semibold text-lg">{{ processUnit?.name }}</div>
        <div class="ml-2 codicon !text-xl" [ngClass]="statusIcon"></div>
      </div>
      <div class="px-5 py-4 ">
        <div>State: {{ processUnit?.state?.state | processUnitState }}</div>
        <div>Location: {{ processUnit?.location }}</div>
        <div>Runtime: {{ processUnit?.runtime_msec | formatDurationMsec }}</div>
      </div>
    </div>
  `
})
export class ProcessUnitCardComponent {
  @Input() processUnit?: ProcessUnit;

  get backgroundColor() {
    const state = this.processUnit?.state.state;
    switch(state) {
      case undefined:
        return '';
      case 'in_progress':
        return 'bg-emerald-700';
      case 'ready':
        return 'bg-sky-800';
      case 'not_online':
        return 'bg-gray-600';
      case 'error':
        return 'bg-rose-700';
      default:
        return UtilMethods.assertNever(state);
    }
  }

  get statusIcon() {
    const state = this.processUnit?.state.state;
    switch(state) {
      case undefined:
        return '';
      case 'in_progress':
        return 'codicon-play-circle';
      case 'ready':
        return 'codicon-pass';
      case 'not_online':
        return 'codicon-circle-slash';
      case 'error':
        return 'codicon-warning';
      default:
        return UtilMethods.assertNever(state);
    }
  }
}
