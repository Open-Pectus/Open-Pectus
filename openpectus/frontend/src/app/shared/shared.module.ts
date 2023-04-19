import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormatDurationMsecPipe } from './formatDurationMsec.pipe';


@NgModule({
  declarations: [
    FormatDurationMsecPipe,
  ],
  exports: [
    FormatDurationMsecPipe,
  ],
  imports: [
    CommonModule,
  ],
})
export class SharedModule {}
