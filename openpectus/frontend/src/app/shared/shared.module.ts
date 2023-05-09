import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormatDurationMsecPipe } from './pipes/format-duration-msec.pipe';
import { ProcessUnitStatePipe } from './pipes/process-unit-state.pipe';
import { TableComponent } from './table.component';


@NgModule({
  declarations: [
    FormatDurationMsecPipe,
    ProcessUnitStatePipe,
    TableComponent,
  ],
  exports: [
    FormatDurationMsecPipe,
    ProcessUnitStatePipe,
    TableComponent,
  ],
  imports: [
    CommonModule,
  ],
})
export class SharedModule {}
