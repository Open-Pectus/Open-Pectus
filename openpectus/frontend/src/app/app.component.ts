import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'app-root',
  template: `
    <div class="bg-red-600">
      test
    </div>
  `
})
export class AppComponent {
}
