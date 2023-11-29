import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { LetDirective, PushPipe } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';

import { BatchJobDetailsComponent } from './batch-job-details.component';
import { BatchJobHeaderComponent } from './batch-job-header.component';
import { CommandExamplesListComponent } from './commands/command-examples-list.component';
import { CommandsComponent } from './commands/commands.component';
import { DetailsRoutingModule } from './details-routing.module';
import { MethodEditorModule } from './method-editor/method-editor.module';
import { DetailsEffects } from './ngrx/details.effects';
import { detailsSlice } from './ngrx/details.reducer';
import { ProcessDiagramComponent } from './process-diagram.component';
import { ProcessPlotModule } from './process-plot/process-plot.module';
import { ProcessValuesModule } from './process-values/process-values.module';
import { RunLogModule } from './run-log/run-log.module';
import { UnitDetailsComponent } from './unit-details.component';
import { UnitControlButtonComponent } from './unit-header/unit-control-button.component';
import { UnitControlsComponent } from './unit-header/unit-controls.component';
import { UnitHeaderComponent } from './unit-header/unit-header.component';

@NgModule({
  imports: [
    CommonModule,
    DetailsRoutingModule,
    StoreModule.forFeature(detailsSlice),
    EffectsModule.forFeature(DetailsEffects),
    ProcessValuesModule,
    MethodEditorModule,
    RunLogModule,
    ProcessPlotModule,
    LetDirective,
    PushPipe,
    UnitDetailsComponent,
    BatchJobDetailsComponent,
    ProcessDiagramComponent,
    CommandsComponent,
    CommandExamplesListComponent,
    UnitHeaderComponent,
    UnitControlButtonComponent,
    UnitControlsComponent,
    BatchJobHeaderComponent,
  ],
})
export class DetailsModule {}
