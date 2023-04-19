import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UnitDetailsComponent } from './unit-details.component';
import { BatchJobDetailsComponent } from './batch-job-details.component';
import { DetailsRoutingModule } from './details-routing.module';


@NgModule({
  declarations: [
    UnitDetailsComponent,
    BatchJobDetailsComponent,
  ],
  imports: [
    CommonModule,
    DetailsRoutingModule,
  ],
})
export class DetailsModule {}
