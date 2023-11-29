import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { LetDirective, PushPipe } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';
import { SharedModule } from '../../shared/shared.module';
import { ProcessPlotEffects } from './ngrx/process-plot.effects';
import { processPlotSlice } from './ngrx/process-plot.reducer';
import { ProcessPlotContainerComponent } from './process-plot-container.component';
import { ProcessPlotComponent } from './process-plot.component';
import { XAxisOverrideDialogComponent } from './x-axis-override-dialog.component';
import { YAxisOverrideDialogComponent } from './y-axis-override-dialog.component';


@NgModule({
  imports: [
    CommonModule,
    SharedModule,
    StoreModule.forFeature(processPlotSlice),
    EffectsModule.forFeature(ProcessPlotEffects),
    PushPipe,
    LetDirective,
    ProcessPlotComponent,
    ProcessPlotContainerComponent,
    YAxisOverrideDialogComponent,
    XAxisOverrideDialogComponent,
  ],
  exports: [
    ProcessPlotComponent,
    ProcessPlotContainerComponent,
  ],
})
export class ProcessPlotModule {}
