import { ChangeDetectionStrategy, Component } from '@angular/core';
import { MswEnablement } from '../msw/msw-enablement';

@Component({
  selector: 'app-msw-enablement',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="text-xs text-slate-400">
      <button class="rounded p-1.5 bg-blue-900"
              (click)="onButtonClick()">
        <label class="flex pointer-events-none">
          <span>MSW:</span>
          <input type="checkbox" [checked]="MswEnablement.isEnabled">
        </label>
      </button>
    </div>
  `,
})
export class MswEnablementComponent {
  protected readonly MswEnablement = MswEnablement;

  onButtonClick() {
    MswEnablement.isEnabled = !MswEnablement.isEnabled;
    setTimeout(() => location.reload());
  }
}
