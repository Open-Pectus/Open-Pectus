import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { PushModule } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';
import { buildWorkerDefinition } from 'monaco-editor-workers';
import getDialogsServiceOverride from 'vscode/service-override/dialogs';
import getNotificationServiceOverride from 'vscode/service-override/notifications';
import { StandaloneServices } from 'vscode/services';
import { DetailsEffects } from '../ngrx/details.effects';
import { detailsFeatureKey, detailsReducer } from '../ngrx/details.reducer';
import { BatchJobDetailsComponent } from './batch-job-details.component';
import { DetailsRoutingModule } from './details-routing.module';
import { MethodEditorComponent } from './method-editor/method-editor.component';
import { MonacoEditorComponent } from './method-editor/monaco-editor.component';
import { UnitDetailsComponent } from './unit-details.component';
import { ProcessValuesComponent } from './process-values/process-values.component';
import { ProcessValueComponent } from './process-values/process-value.component';
import { ProcessValueEditorComponent } from './process-values/process-value-editor.component';
import { ProcessValueCommandsComponent } from './process-values/process-value-commands.component';

StandaloneServices.initialize({
  ...getNotificationServiceOverride(),
  ...getDialogsServiceOverride(),
});

buildWorkerDefinition('./assets/monaco-editor-workers/workers', window.location.origin, false);

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
  ],
  imports: [
    CommonModule,
    DetailsRoutingModule,
    PushModule,
    StoreModule.forFeature(detailsFeatureKey, detailsReducer),
    EffectsModule.forFeature([DetailsEffects]),
  ],
})
export class DetailsModule {}
