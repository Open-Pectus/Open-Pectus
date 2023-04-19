import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-unit-details',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <p>
      unit-details works!
    </p>
  `,
})
export class UnitDetailsComponent {

}
