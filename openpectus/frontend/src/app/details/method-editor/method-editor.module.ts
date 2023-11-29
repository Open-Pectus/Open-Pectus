import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { LetDirective, PushPipe } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';

import { MethodEditorComponent } from './method-editor.component';
import { MonacoEditorComponent } from './monaco-editor.component';
import { MethodEditorEffects } from './ngrx/method-editor.effects';
import { methodEditorSlice } from './ngrx/method-editor.reducer';


@NgModule({
  imports: [
    CommonModule,
    StoreModule.forFeature(methodEditorSlice),
    EffectsModule.forFeature(MethodEditorEffects),
    LetDirective,
    PushPipe,
    MethodEditorComponent,
    MonacoEditorComponent,
  ],
  exports: [
    MethodEditorComponent,
  ],
})
export class MethodEditorModule {}
