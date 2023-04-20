import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-recent-batch-jobs',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="w-full h-96 bg-vscode-backgroundgrey"></div>
  `,
})
export class RecentBatchJobsComponent {

}
