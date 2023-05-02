import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UnitDetailsComponent } from './unit-details.component';
import { BatchJobDetailsComponent } from './batch-job-details.component';
import { DetailsRoutingModule } from './details-routing.module';
import { MethodEditorComponent } from './method-editor/method-editor.component';
import { MonacoEditorComponent } from './method-editor/monaco-editor.component';


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
