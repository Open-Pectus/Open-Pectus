import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { buildWorkerDefinition } from 'monaco-editor-workers';
import getDialogsServiceOverride from 'vscode/service-override/dialogs';
import getNotificationServiceOverride from 'vscode/service-override/notifications';
import { StandaloneServices } from 'vscode/services';
import { BatchJobDetailsComponent } from './batch-job-details.component';
import { DetailsRoutingModule } from './details-routing.module';
import { MethodEditorComponent } from './method-editor/method-editor.component';
import { MonacoEditorComponent } from './method-editor/monaco-editor.component';
import { UnitDetailsComponent } from './unit-details.component';

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
  ],
  imports: [
    CommonModule,
    DetailsRoutingModule,
  ],
})
export class DetailsModule {}
