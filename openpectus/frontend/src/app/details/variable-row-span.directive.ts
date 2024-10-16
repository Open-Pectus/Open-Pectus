import { AfterViewInit, Directive, ElementRef, HostBinding, OnDestroy } from '@angular/core';

@Directive({
  selector: '[appVariableRowSpan]',
  standalone: true,
})
export class VariableRowSpanDirective implements AfterViewInit, OnDestroy {
  collapsedElementHeight = 54;
  rowGap = 32;
  private contentHeight = 0;
  private observer = new ResizeObserver((entries: ResizeObserverEntry[], _: ResizeObserver) => {
    this.contentHeight = entries.at(0)?.contentRect?.height ?? 0;
  });

  constructor(private ref: ElementRef<HTMLElement>) {}

  @HostBinding('style.grid-row') get rowSpan() {
    const myHeight = this.collapsedElementHeight + this.contentHeight + this.rowGap;
    const heightPerRow = this.rowGap;
    const span = Math.ceil(myHeight / heightPerRow);
    return `span ${span} / span ${span}`;
  }

  ngAfterViewInit() {
    const contentElement = this.ref.nativeElement.querySelector('.overflow-hidden');
    if(contentElement === null) return;
    this.observer.observe(contentElement);
  }

  ngOnDestroy() {
    this.observer.disconnect();
  }
}
