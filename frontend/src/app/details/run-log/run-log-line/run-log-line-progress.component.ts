import { DecimalPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'app-run-log-line-progress',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [DecimalPipe],
  template: `
    <div class="border-gray-400 bg-white border rounded-md overflow-hidden w-28 h-full flex items-center relative">
      @let _value = value();
      @if (_value !== undefined) {
        <div class="bg-sky-600 saturate-50 h-full overflow-visible flex items-center"
             [style.width.%]="_value * 100">
        </div>
      }
      @if (_value === undefined) {
        <div class="bg-sky-600 saturate-50 h-full rounded-md w-1/3 relative animate-ping-pong-x"
        ></div>
      }
      @if (_value !== undefined) {
        <span class="absolute text-xs mx-1 font-semibold"
              [class.left-0]="_value >= .5" [class.right-0]="_value < .5"
              [class.text-white]="_value >= .5" [class.text-black]="_value < .5"
        >{{ _value * 100 | number:'1.1-1' }} %</span>
      }
    </div>
  `
})
export class RunLogLineProgressComponent {
  readonly value = input<number>();
}
