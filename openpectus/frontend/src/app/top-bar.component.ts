import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-top-bar',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="w-full h-14 flex items-center bg-sky-900 text-white relative">
      <div class="absolute-center text-3xl font-bold">Open Pectus</div>
      <div class="absolute right-4 codicon codicon-account !text-3xl"></div>

    </div>
  `,
})
export class TopBarComponent {

}
