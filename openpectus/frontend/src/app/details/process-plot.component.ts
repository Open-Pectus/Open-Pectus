import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import Plotly, { LayoutAxis, PlotData } from 'plotly.js-basic-dist-min';
import { combineLatest, Subject, takeUntil } from 'rxjs';
import { ProcessValue } from '../api';
import { DetailsSelectors } from './ngrx/details.selectors';
import { PlotlyDefaults } from './plotly-defaults';

@Component({
  selector: 'app-process-plot',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400">
      <div content class="h-full" #plot></div>
    </app-collapsible-element>`,
})
export class ProcessPlotComponent implements AfterViewInit, OnDestroy {
  processUnit = this.store.select(DetailsSelectors.processUnit);
  processValuesLog = this.store.select(DetailsSelectors.processValuesLog);
  @ViewChild('plot', {static: true}) plotElement?: ElementRef<HTMLDivElement>;
  private componentDestroyed = new Subject<void>();
  private processValueNames = ['FT01 Flow', 'TT01', 'FT01 Flow.PV'];

  constructor(private store: Store) {}

  ngAfterViewInit() {
    if(this.plotElement === undefined) throw Error('Missing plot div element!');
    const plotElement = this.plotElement;
    combineLatest([this.processValuesLog, this.processUnit]).pipe(takeUntil(this.componentDestroyed)).subscribe(
      ([processValuesLog, processUnit]) => {
        const values = this.processValueNames.map((name, index) => this.extractPlotDataFromLog(processValuesLog, name, index));
        const units = this.processValueNames.map(name => this.extractUnitsFromLog(processValuesLog, name));
        const yAxes = this.convertToAxes(units);
        Plotly.react(plotElement.nativeElement, values, {
          autosize: true,
          title: processUnit?.name,
          ...yAxes,
          xaxis: {domain: [0, this.processValueNames.length > 2 ? 1 - (this.processValueNames.length - 2) * .1 : 1]},
          legend: {y: 100, x: 0},
          uirevision: 'true',
        }, {
          responsive: true,
        });
      });
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  private extractPlotDataFromLog(processValuesLog: ProcessValue[][], name: string, pvIndex: number) {
    return processValuesLog.reduce((prev, curr, index) => {
      const processValue = curr.find(processValue => processValue.name === name);
      if(processValue === undefined || typeof processValue.value !== 'number') return prev;
      return {
        ...prev,
        x: [...prev.x, index],
        y: [...prev.y, processValue.value],
        name,
        yaxis: 'y' + (pvIndex > 0 ? pvIndex + 1 : ''),
      };
    }, {x: [], y: [], type: 'scatter'} as { x: number[], y: number[] } & Partial<PlotData>);
  }

  private extractUnitsFromLog(processValuesLog: ProcessValue[][], name: string) {
    return processValuesLog[0]?.find(processValue => processValue.name === name)?.value_unit;
  }

  private convertToAxes(titles: (string | undefined)[]) {
    const object = {};
    titles.forEach((title, index) => {
      Object.assign(object, {
        ['yaxis' + (index > 0 ? index + 1 : '')]: {
          title,
          side: (index > 0 ? 'right' : 'left'),
          overlaying: index > 0 ? 'y' : 'free',
          anchor: index > 1 ? 'free' : undefined,
          position: index > 1 ? 1 : undefined,
          titlefont: {color: PlotlyDefaults.colors[index]},
          tickfont: {color: PlotlyDefaults.colors[index]},
        } as Partial<LayoutAxis>,
      });
    });
    return object;
  }
}
