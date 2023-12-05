import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { MswEnablement } from '../msw/msw-enablement';
import { FrontendPubsubService } from './api';

@Component({
  selector: 'app-msw-enablement',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
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
export class MswEnablementComponent implements OnInit {
  protected readonly MswEnablement = MswEnablement;

  constructor(private pubSubService: FrontendPubsubService) {}

  ngOnInit() {
    if(MswEnablement.isEnabled) {
      setInterval(() => this.pubSubService.triggerPublishMsw().subscribe(), 3000);
    }
  }

  onButtonClick() {
    MswEnablement.isEnabled = !MswEnablement.isEnabled;
    setTimeout(() => location.reload());
  }
}
