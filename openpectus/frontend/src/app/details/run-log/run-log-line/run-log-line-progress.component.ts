import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

@Component({
  selector: 'app-run-log-line-progress',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="border-slate-400 bg-slate-100 border rounded-md overflow-hidden w-28 h-full">
      <div class="bg-sky-500 saturate-50 h-full" [style.width.%]="value * 100" *ngIf="value !== undefined"></div>
      <div class="bg-sky-500 saturate-50 h-full rounded-md w-1/3 relative animate-ping-pong-x"
           *ngIf="value === undefined"></div>
    </div>
  `,
  styles: [
    `@keyframes pingpong {
       0% {
         transform: translateX(0);
         left: 0;
       }
       100% {
         transform: translateX(-100%);
         left: 100%;
       }
     }`,
  ],
})
export class RunLogLineProgressComponent {
  @Input() value?: number;
}
