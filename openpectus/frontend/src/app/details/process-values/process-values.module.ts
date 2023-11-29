import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { LetDirective, PushPipe } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';

import { ProcessValuesEffects } from './ngrx/process-values.effects';
import { processValuesSlice } from './ngrx/process-values.reducer';
import { ProcessValueCommandButtonComponent } from './process-value-command-button.component';
import { ProcessValueCommandChoiceComponent } from './process-value-command-choice.component';
import { ProcessValueCommandsComponent } from './process-value-commands.component';
import { ProcessValueEditorComponent } from './process-value-editor.component';
import { ProcessValueComponent } from './process-value.component';
import { ProcessValuesComponent } from './process-values.component';


@NgModule({
  imports: [
    CommonModule,
    StoreModule.forFeature(processValuesSlice),
    EffectsModule.forFeature(ProcessValuesEffects),
    LetDirective,
    PushPipe,
    ProcessValuesComponent,
    ProcessValueComponent,
    ProcessValueEditorComponent,
    ProcessValueCommandsComponent,
    ProcessValueCommandChoiceComponent,
    ProcessValueCommandButtonComponent,
  ],
  exports: [
    ProcessValuesComponent,
  ],
})
export class ProcessValuesModule {}
