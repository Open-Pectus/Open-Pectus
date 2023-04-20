import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormatDurationMsecPipe } from './pipes/format-duration-msec.pipe';
import { ProcessUnitStatePipe } from './pipes/process-unit-state.pipe';


@NgModule({
  declarations: [
    FormatDurationMsecPipe,
    ProcessUnitStatePipe,
  ],
  exports: [
    FormatDurationMsecPipe,
    ProcessUnitStatePipe,
  ],
  imports: [
    CommonModule,
  ],
})
export class SharedModule {}
