import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { LetDirective, PushPipe } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';
import { SharedModule } from '../../shared/shared.module';
import { ProcessValuesEffects } from './ngrx/process-values.effects';
import { processValuesSlice } from './ngrx/process-values.reducer';
import { ProcessValueCommandsComponent } from './process-value-commands.component';
import { ProcessValueEditorComponent } from './process-value-editor.component';
import { ProcessValueComponent } from './process-value.component';
import { ProcessValuesComponent } from './process-values.component';


@NgModule({
  declarations: [
    ProcessValuesComponent,
    ProcessValueComponent,
    ProcessValueEditorComponent,
    ProcessValueCommandsComponent,
  ],
  imports: [
    CommonModule,
    StoreModule.forFeature(processValuesSlice),
    EffectsModule.forFeature(ProcessValuesEffects),
    LetDirective,
    PushPipe,
    SharedModule,
  ],
  exports: [
    ProcessValuesComponent,
  ],
})
export class ProcessValuesModule {}
