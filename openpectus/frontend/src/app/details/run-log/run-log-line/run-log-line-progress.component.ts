import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

@Component({
  selector: 'app-run-log-line-progress',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="border-slate-400 bg-slate-100 border rounded-md overflow-hidden w-28 h-full flex items-center relative"
         [title]="title">
      <div class="bg-sky-600 saturate-50 h-full overflow-visible flex items-center"
           [style.width.%]="value * 100" *ngIf="value !== undefined">
      </div>
      <div class="bg-sky-600 saturate-50 h-full rounded-md w-1/3 relative animate-ping-pong-x"
           *ngIf="value === undefined"></div>
      <span class="absolute text-xs mx-1 font-semibold"
            [class.left-0]="value >= .5" [class.right-0]="value < .5"
            [class.text-white]="value >= .5" [class.text-black]="value < .5"
            *ngIf="value !== undefined">{{value * 100 | number:'1.1-1'}} %</span>

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

  get title() {
    if(this.value === undefined) return 'no value';
    return `${this.value * 100} %`;
  }
}
