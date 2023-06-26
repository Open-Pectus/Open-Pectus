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
import { MethodEditorComponent } from './method-editor/method-editor.component';
import { MonacoEditorComponent } from './method-editor/monaco-editor.component';
import { DetailsEffects } from './ngrx/details.effects';
import { detailsFeatureKey, detailsReducer } from './ngrx/details.reducer';
import { ProcessDiagramComponent } from './process-diagram.component';
import { ProcessPlotComponent } from './process-plot.component';
import { ProcessValueCommandsComponent } from './process-values/process-value-commands.component';
import { ProcessValueEditorComponent } from './process-values/process-value-editor.component';
import { ProcessValueComponent } from './process-values/process-value.component';
import { ProcessValuesComponent } from './process-values/process-values.component';
import { RunLogAdditionalValuesComponent } from './run-log/run-log-additional-values.component';
import { RunLogLineComponent } from './run-log/run-log-line.component';
import { RunLogComponent } from './run-log/run-log.component';
import { UnitDetailsComponent } from './unit-details.component';
import { UnitHeaderComponent } from './unit-header.component';

@NgModule({
  declarations: [
    UnitDetailsComponent,
    BatchJobDetailsComponent,
    MethodEditorComponent,
    MonacoEditorComponent,
    ProcessValuesComponent,
    ProcessValueComponent,
    ProcessValueEditorComponent,
    ProcessValueCommandsComponent,
    ProcessDiagramComponent,
    CommandsComponent,
    CommandExamplesListComponent,
    UnitHeaderComponent,
    RunLogComponent,
    RunLogLineComponent,
    ProcessPlotComponent,
    RunLogAdditionalValuesComponent,
  ],
  imports: [
    CommonModule,
    DetailsRoutingModule,
    StoreModule.forFeature(detailsFeatureKey, detailsReducer),
    EffectsModule.forFeature([DetailsEffects]),
    SharedModule,
    LetDirective,
    PushPipe,
  ],
})
export class DetailsModule {}
