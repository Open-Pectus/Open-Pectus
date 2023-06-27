import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { LetDirective, PushPipe } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';
import { SharedModule } from '../shared/shared.module';
import { BatchJobDetailsComponent } from './batch-job-details.component';
import { CommandExamplesListComponent } from './commands/command-examples-list.component';
import { CommandsComponent } from './commands/commands.component';
import { DetailsRoutingModule } from './details-routing.module';
import { MethodEditorModule } from './method-editor/method-editor.module';
import { DetailsEffects } from './ngrx/details.effects';
import { detailsSlice } from './ngrx/details.reducer';
import { ProcessDiagramComponent } from './process-diagram.component';
import { ProcessPlotComponent } from './process-plot.component';
import { ProcessValuesModule } from './process-values/process-values.module';
import { RunLogModule } from './run-log/run-log.module';
import { UnitDetailsComponent } from './unit-details.component';
import { UnitHeaderComponent } from './unit-header.component';

@NgModule({
  declarations: [
    UnitDetailsComponent,
    BatchJobDetailsComponent,
    ProcessDiagramComponent,
    CommandsComponent,
    CommandExamplesListComponent,
    UnitHeaderComponent,
    ProcessPlotComponent,
  ],
  imports: [
    CommonModule,
    DetailsRoutingModule,
    StoreModule.forFeature(detailsSlice),
    EffectsModule.forFeature(DetailsEffects),
    ProcessValuesModule,
    MethodEditorModule,
    RunLogModule,
    SharedModule,
    LetDirective,
    PushPipe,
  ],
})
export class DetailsModule {}
