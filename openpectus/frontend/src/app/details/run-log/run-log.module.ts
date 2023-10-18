import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { LetDirective, PushPipe } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';
import { SharedModule } from '../../shared/shared.module';
import { RunLogEffects } from './ngrx/run-log.effects';
import { runLogSlice } from './ngrx/run-log.reducer';
import { RunLogAdditionalValuesComponent } from './run-log-additional-values.component';
import { RunLogFiltersComponent } from './run-log-filters.component';
import { RunLogHeaderComponent } from './run-log-header.component';
import { RunLogLineButtonComponent } from './run-log-line/run-log-line-button.component';
import { RunLogLineCancelButtonComponent } from './run-log-line/run-log-line-cancel-button.component';
import { RunLogLineForceButtonComponent } from './run-log-line/run-log-line-force-button.component';
import { RunLogLineComponent } from './run-log-line/run-log-line.component';
import { RunLogComponent } from './run-log.component';


@NgModule({
  declarations: [
    RunLogComponent,
    RunLogLineComponent,
    RunLogFiltersComponent,
    RunLogHeaderComponent,
    RunLogAdditionalValuesComponent,
    RunLogLineForceButtonComponent,
    RunLogLineCancelButtonComponent,
    RunLogLineButtonComponent,
  ],
  imports: [
    CommonModule,
    StoreModule.forFeature(runLogSlice),
    EffectsModule.forFeature(RunLogEffects),
    SharedModule,
    PushPipe,
    LetDirective,
  ],
  exports: [
    RunLogComponent,
  ],
})
export class RunLogModule {}
