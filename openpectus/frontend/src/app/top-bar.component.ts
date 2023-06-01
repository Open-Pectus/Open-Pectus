import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-top-bar',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="w-full h-14 flex items-center bg-sky-900 text-white relative">
      <app-msw-enablement class="absolute left-4"></app-msw-enablement>
      <button class="absolute-center text-3xl font-bold" (click)="navigateToRoot()">Open Pectus</button>
      <div class="absolute right-4 codicon codicon-account !text-3xl"></div>
    </div>
  `,
})
export class TopBarComponent {
  constructor(private router: Router) {}

  navigateToRoot() {
    this.router.navigate(['/']).then();
  }
}
