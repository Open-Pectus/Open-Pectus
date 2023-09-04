import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { LetDirective, PushPipe } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';
import { SharedModule } from '../../shared/shared.module';
import { ProcessPlotEffects } from './ngrx/process-plot.effects';
import { processPlotSlice } from './ngrx/process-plot.reducer';
import { ProcessPlotContainerComponent } from './process-plot-container.component';
import { ProcessPlotD3Component } from './process-plot-d3.component';
import { YAxisOverrideDialogComponent } from './yaxis-override-dialog.component';


@NgModule({
  declarations: [
    ProcessPlotD3Component,
    ProcessPlotContainerComponent,
    YAxisOverrideDialogComponent,
  ],
  imports: [
    CommonModule,
    SharedModule,
    StoreModule.forFeature(processPlotSlice),
    EffectsModule.forFeature(ProcessPlotEffects),
    PushPipe,
    LetDirective,
  ],
  exports: [
    ProcessPlotD3Component,
    ProcessPlotContainerComponent,
  ],
})
export class ProcessPlotModule {}
