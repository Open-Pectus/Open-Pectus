import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import Plotly from 'plotly.js-basic-dist-min';
import { filter, Subject, takeUntil } from 'rxjs';
import { UtilMethods } from '../../shared/util-methods';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';

@Component({
  selector: 'app-process-plot',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400" (collapseStateChanged)="collapsed = $event">
      <div content class="h-full" #plot *ngIf="!collapsed"></div>
    </app-collapsible-element>`,
})
export class ProcessPlotComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('plot', {static: false}) plotElement?: ElementRef<HTMLDivElement>;
  protected collapsed = false;
  // private processValuesLog = this.store.select(DetailsSelectors.processValuesLog);
  // private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration);
  private plots = this.store.select(ProcessPlotSelectors.processValuePlots);
  private layout = this.store.select(ProcessPlotSelectors.processPlotLayout);
  private componentDestroyed = new Subject<void>();

  // private processValueNames = ['FT01 Flow', 'TT01', 'PU01 Speed'];

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentInitialized());
  }

  ngAfterViewInit() {
    if(this.plotElement === undefined) throw Error('missing plot dom element!');
    const element = this.plotElement?.nativeElement;
    this.layout.pipe(filter(UtilMethods.isNotNullOrUndefined), takeUntil(this.componentDestroyed)).subscribe(layout => {
      // Plotly.newPlot(element, [], layout).then(() => {
      this.plots.pipe(takeUntil(this.componentDestroyed)).subscribe(plots => {
        Plotly.react(element, plots, layout, {responsive: true});
      });
      // });
    });


    // combineLatest([this.processValuesLog, this.plotConfiguration]).pipe(
    //   filter(() => !this.collapsed),
    //   takeUntil(this.componentDestroyed),
    // ).subscribe(
    //   ([processValuesLog, plotConfiguration]) => {
    //     // const values = this.processValueNames.map((name, index) => this.extractPlotDataFromLog(processValuesLog, name, index));
    //     // const units = this.processValueNames.map(name => this.extractUnitsFromLog(processValuesLog, name));
    //     // const yAxes = this.convertToAxes(units);
    //     // Plotly.react(this.plotElement.nativeElement, values, {
    //     //   autosize: true,
    //     //   ...yAxes,
    //     //   xaxis: {domain: [0, this.processValueNames.length > 2 ? 1 - (this.processValueNames.length - 2) * .1 : 1]},
    //     //   legend: {y: 100, x: 0},
    //     //   uirevision: 'true',
    //     // }, {
    //     //   responsive: true,
    //     // });
    //   });
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  // private extractPlotDataFromLog(processValuesLog: ProcessValue[][], name: string, pvIndex: number) {
  //   return processValuesLog.reduce((prev, curr, index) => {
  //     const processValue = curr.find(processValue => processValue.name === name);
  //     if(processValue === undefined || typeof processValue.value !== 'number') return prev;
  //     return {
  //       ...prev,
  //       x: [...prev.x, index],
  //       y: [...prev.y, processValue.value],
  //       name,
  //       yaxis: 'y' + (pvIndex > 0 ? pvIndex + 1 : ''),
  //     };
  //   }, {x: [], y: [], type: 'scatter'} as { x: number[], y: number[] } & Partial<PlotData>);
  // }

  // private extractUnitsFromLog(processValuesLog: ProcessValue[][], name: string) {
  //   return processValuesLog[0]?.find(processValue => processValue.name === name)?.value_unit;
  // }

  // private convertToAxes(titles: (string | undefined)[]) {
  //   const object = {};
  //   titles.forEach((title, index) => {
  //     Object.assign(object, {
  //       ['yaxis' + (index > 0 ? index + 1 : '')]: {
  //         title,
  //         side: (index > 0 ? 'right' : 'left'),
  //         overlaying: index > 0 ? 'y' : 'free',
  //         anchor: index > 1 ? 'free' : undefined,
  //         position: index > 1 ? 1 : undefined,
  //         titlefont: {color: PlotlyDefaults.colors[index]},
  //         tickfont: {color: PlotlyDefaults.colors[index]},
  //       } as Partial<LayoutAxis>,
  //     });
  //   });
  //   return object;
  // }
}
