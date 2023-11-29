import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { CollapsibleElementComponent } from './collapsible-element.component';
import { FormatDurationMsecPipe } from './pipes/format-duration-msec.pipe';
import { ProcessUnitStatePipe } from './pipes/process-unit-state.pipe';
import { ProcessValuePipe } from './pipes/process-value.pipe';
import { SafeHtmlPipe } from './pipes/safe-html.pipe';
import { TableComponent } from './table.component';


@NgModule({
  exports: [
    FormatDurationMsecPipe,
    ProcessUnitStatePipe,
    TableComponent,
    CollapsibleElementComponent,
    ProcessValuePipe,
    SafeHtmlPipe,
  ],
  imports: [
    CommonModule,
    FormatDurationMsecPipe,
    ProcessUnitStatePipe,
    TableComponent,
    CollapsibleElementComponent,
    ProcessValuePipe,
    SafeHtmlPipe,
  ],
})
export class SharedModule {}
