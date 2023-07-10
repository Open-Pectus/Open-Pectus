import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import Plotly, { LayoutAxis, PlotData } from 'plotly.js-basic-dist-min';
import { combineLatest, filter, Subject, takeUntil } from 'rxjs';
import { ProcessValue } from '../api';
import { DetailsSelectors } from './ngrx/details.selectors';
import { PlotlyDefaults } from './plotly-defaults';

@Component({
  selector: 'app-process-plot',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400" (collapseStateChanged)="collapsed = $event">
      <div content class="h-full" #plot *ngIf="!collapsed"></div>
    </app-collapsible-element>`,
})
export class ProcessPlotComponent implements AfterViewInit, OnDestroy {
  processUnit = this.store.select(DetailsSelectors.processUnit);
  processValuesLog = this.store.select(DetailsSelectors.processValuesLog);
  @ViewChild('plot', {static: false}) plotElement?: ElementRef<HTMLDivElement>;
  protected collapsed = false;
  private componentDestroyed = new Subject<void>();
  private processValueNames = ['FT01 Flow', 'TT01', 'PU01 Speed'];

  constructor(private store: Store) {}

  ngAfterViewInit() {
    combineLatest([this.processValuesLog, this.processUnit]).pipe(
      filter(() => !this.collapsed),
      takeUntil(this.componentDestroyed),
    ).subscribe(
      ([processValuesLog, processUnit]) => {
        if(this.plotElement === undefined) return;
        const values = this.processValueNames.map((name, index) => this.extractPlotDataFromLog(processValuesLog, name, index));
        const units = this.processValueNames.map(name => this.extractUnitsFromLog(processValuesLog, name));
        const yAxes = this.convertToAxes(units);
        Plotly.react(this.plotElement.nativeElement, values, {
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