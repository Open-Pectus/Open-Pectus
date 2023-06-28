import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';
import { SharedModule } from '../../shared/shared.module';
import { ProcessPlotEffects } from './ngrx/process-plot.effects';
import { processPlotSlice } from './ngrx/process-plot.reducer';
import { ProcessPlotChartjsComponent } from './process-plot-chartjs.component';
import { ProcessPlotPlotlyComponent } from './process-plot-plotly.component';


@NgModule({
  declarations: [
    ProcessPlotPlotlyComponent,
    ProcessPlotChartjsComponent,
  ],
  imports: [
    CommonModule,
    SharedModule,
    StoreModule.forFeature(processPlotSlice),
    EffectsModule.forFeature(ProcessPlotEffects),
  ],
  exports: [
    ProcessPlotPlotlyComponent,
    ProcessPlotChartjsComponent,
  ],
})
export class ProcessPlotModule {}
