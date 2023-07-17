import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import { axisY, frame, lineY, plot } from '@observablehq/plot';
import { combineLatest, filter, Subject, takeUntil } from 'rxjs';
import { PlotConfiguration, ProcessValue } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { DetailsSelectors } from '../ngrx/details.selectors';
import { ProcessPlotActions } from './ngrx/process-plot.actions';
import { ProcessPlotSelectors } from './ngrx/process-plot.selectors';

@Component({
  selector: 'app-process-plot-plot',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Plot'" [heightResizable]="true" [contentHeight]="400"
                             (collapseStateChanged)="isCollapsed = $event">
      <div content class="h-full" #plot *ngIf="!isCollapsed"></div>

    </app-collapsible-element>
  `,
})
export class ProcessPlotPlotComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('plot', {static: false}) plotElement?: ElementRef<HTMLElement>;
  protected isCollapsed = false;
  private processValuesLog = this.store.select(DetailsSelectors.processValuesLog);
  private plotConfiguration = this.store.select(ProcessPlotSelectors.plotConfiguration).pipe(filter(UtilMethods.isNotNullOrUndefined));
  private plots = combineLatest([this.processValuesLog, this.plotConfiguration]);
  // plotHtml = this.plots.pipe(filter(() => !this.isCollapsed), map(([processValueLog, plotConfiguration]) => {
  //   return plot({
  //     marks: [
  //       frame(),
  //     ],
  //   });
  // }));
  private componentDestroyed = new Subject<void>();

  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(ProcessPlotActions.processPlotComponentInitialized());
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  ngAfterViewInit() {
    this.plots.pipe(filter(() => !this.isCollapsed), takeUntil(this.componentDestroyed)).subscribe(([processValueLog, plotConfiguration]) => {
      if(this.plotElement === undefined) return;
      this.plotElement.nativeElement.replaceChildren(plot({
        marks: [
          frame(),
          ...this.convertData(plotConfiguration, processValueLog),
        ],
      }));
    });
  }

  convertData(plotConfiguration: PlotConfiguration, processValueLog: ProcessValue[][]) {
    return plotConfiguration.sub_plots.flatMap((subPlot, subPlotIndex) => {
      return subPlot.axes.flatMap((axis, axisIndex) => {
        return [
          axisY({
            anchor: axisIndex === 0 ? 'left' : 'right',
            color: axis.color,
            // dx: (axisIndex - 1) * 25,
            insetLeft: (axisIndex - 1) * 10,
          }),
          ...axis.process_value_names.flatMap(name => {
            return lineY(processValueLog
                .map(processValues => processValues.find(processValue => processValue.name === name)?.value)
                .filter(UtilMethods.isNotNullOrUndefined).filter(UtilMethods.isNumber)
                .map((processValue, valueIndex) => ({x: valueIndex, y: processValue})),
              {x: 'x', y: 'y', stroke: axis.color});
          })];
      });
    });
  }
}
