import { AfterViewInit, ChangeDetectorRef, Directive, ElementRef, HostBinding, OnDestroy } from '@angular/core';

@Directive({
  selector: '[appVariableRowSpan]',
})
export class VariableRowSpanDirective implements AfterViewInit, OnDestroy {
  private rowSpan = 0;
  private collapsibleElement?: HTMLElement;
  private readonly rowGap = 32;
  private resizeObserver = new ResizeObserver(() => {
    const collapsibleElementHeight = this.collapsibleElement?.getBoundingClientRect().height ?? 0;
    this.rowSpan = Math.ceil(collapsibleElementHeight) + this.rowGap;
    this.cd.markForCheck();
  });

  constructor(private ref: ElementRef<HTMLElement>,
              private cd: ChangeDetectorRef) {}

  @HostBinding('style.grid-row') get gridRow() {
    return `span ${this.rowSpan} / span ${this.rowSpan}`;
  }

  ngAfterViewInit() {
    this.collapsibleElement = this.ref.nativeElement.querySelector('app-collapsible-element') ?? undefined;
    const contentContainer = this.ref.nativeElement.querySelector('[content]')?.parentElement ?? null;
    if(contentContainer === null) return;
    this.resizeObserver.observe(contentContainer);
  }

  ngOnDestroy() {
    this.resizeObserver.disconnect();
  }
}
