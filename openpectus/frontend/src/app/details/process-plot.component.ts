import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import Plotly from 'plotly.js-basic-dist-min';
import { Subject, takeUntil } from 'rxjs';
import { ProcessValue } from '../api';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-process-plot',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400">
      <div content class="h-full" #plot></div>
    </app-collapsible-element>`,
})
export class ProcessPlotComponent implements AfterViewInit, OnDestroy {
  processValuesLog = this.store.select(DetailsSelectors.processValuesLog);
  @ViewChild('plot', {static: true}) plotElement?: ElementRef<HTMLDivElement>;
  private componentDestroyed = new Subject<void>();

  constructor(private store: Store) {}

  ngAfterViewInit() {
    if(this.plotElement === undefined) throw Error('Missing plot div element!');
    const plotElement = this.plotElement;
    this.processValuesLog.pipe(takeUntil(this.componentDestroyed)).subscribe(processValuesLog => {
      const values = this.convertLogToPlotData(processValuesLog);
      Plotly.react(plotElement.nativeElement, [values], {autosize: true}, {});
    });
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  private convertLogToPlotData(processValuesLog: ProcessValue[][]) {
    return processValuesLog.reduce((prev, curr, index, array) => {
      const processValue = curr.find(processValue => processValue.name === 'FT01 Flow');
      if(processValue === undefined || typeof processValue.value !== 'number') return prev;
      return {
        x: prev.x.concat(index),
        y: prev.y.concat(processValue.value),
        type: prev.type,
      };
    }, {x: [] as number[], y: [] as number[], type: 'scatter' as const});
  }
}
