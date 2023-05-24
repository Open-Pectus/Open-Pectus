import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-unit-details',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex justify-center">
      <div class="flex flex-col max-w-5xl w-full p-8 gap-8">
        <app-unit-header></app-unit-header>
        <app-process-values></app-process-values>
        <app-method-editor></app-method-editor>
        <app-commands></app-commands>
        <!-- Plot -->
        <app-process-diagram></app-process-diagram>
      </div>
    </div>
  `,
})
export class UnitDetailsComponent {

}
