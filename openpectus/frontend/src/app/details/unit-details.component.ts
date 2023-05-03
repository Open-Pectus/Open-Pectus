import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-unit-details',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex justify-center">
      <div class="flex flex-col max-w-5xl w-full mx-8">
        <!-- Name, Controls, Role -->
        <app-process-values></app-process-values>
        <app-method-editor></app-method-editor>
        <!-- Plot -->
        <!-- Process Diagram -->
      </div>
    </div>
  `,
})
export class UnitDetailsComponent {

}
