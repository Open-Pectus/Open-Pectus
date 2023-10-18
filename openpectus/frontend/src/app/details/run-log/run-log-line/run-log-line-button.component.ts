import { ChangeDetectionStrategy, ChangeDetectorRef, Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-run-log-line-button',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button class="flex items-center gap-1.5 rounded-md px-2 py-1 text-white"
            [ngClass]="isConfirming ? 'bg-amber-600' : colorClass"
            (click)="onClick()">
      <i class="codicon" [ngClass]="codiconClass"></i>
      {{isConfirming ? 'Confirm' : ''}} {{buttonText}}{{isConfirming ? '?' : ''}}
    </button>
  `,
})
export class RunLogLineButtonComponent {
  @Input() codiconClass?: string;
  @Input() colorClass?: string;
  @Input() buttonText?: string;
  @Output() confirmedClick = new EventEmitter<void>();
  protected isConfirming = false;

  constructor(private cd: ChangeDetectorRef) {}

  onClick() {
    if(this.isConfirming) this.confirmedClick.emit();
    this.isConfirming = !this.isConfirming;
    if(this.isConfirming) {
      setTimeout(() => {
        this.isConfirming = false;
        this.cd.markForCheck();
      }, 4000);
    }
  }
}
