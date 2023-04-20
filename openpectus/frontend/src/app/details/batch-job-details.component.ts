import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-batch-job-details',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <p>
      batch-job-details works!
    </p>
  `,
})
export class BatchJobDetailsComponent {

}
