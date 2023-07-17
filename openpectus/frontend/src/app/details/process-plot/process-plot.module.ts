import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { PushPipe } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';
import { SharedModule } from '../../shared/shared.module';
import { ProcessPlotEffects } from './ngrx/process-plot.effects';
import { processPlotSlice } from './ngrx/process-plot.reducer';
import { ProcessPlotChartjsComponent } from './process-plot-chartjs.component';
import { ProcessPlotPlotComponent } from './process-plot-plot.component';
import { ProcessPlotPlotlyComponent } from './process-plot-plotly.component';


@NgModule({
  declarations: [
    ProcessPlotPlotlyComponent,
    ProcessPlotChartjsComponent,
    ProcessPlotPlotComponent,
  ],
  imports: [
    CommonModule,
    SharedModule,
    StoreModule.forFeature(processPlotSlice),
    EffectsModule.forFeature(ProcessPlotEffects),
    PushPipe,
  ],
  exports: [
    ProcessPlotPlotlyComponent,
    ProcessPlotChartjsComponent,
    ProcessPlotPlotComponent,
  ],
})
export class ProcessPlotModule {}
