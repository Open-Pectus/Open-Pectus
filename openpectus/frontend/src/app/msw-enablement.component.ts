import { ChangeDetectionStrategy, Component } from '@angular/core';
import { MswEnablement } from '../msw/msw-enablement';

@Component({
  selector: 'app-msw-enablement',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="text-xs text-slate-400">
      You are <i>{{MswEnablement.isEnabled ? '' : 'not'}}</i> using MSW
      <button class="rounded p-1.5 ml-1 bg-blue-900" (click)="MswEnablement.isEnabled = !MswEnablement.isEnabled; location.reload()">
        {{MswEnablement.isEnabled ? 'Disable' : 'Enable'}}
      </button>
    </div>
  `,
})
export class MswEnablementComponent {
  protected readonly MswEnablement = MswEnablement;
  protected readonly location = location;
}
