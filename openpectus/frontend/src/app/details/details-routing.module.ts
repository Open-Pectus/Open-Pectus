import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BatchJobDetailsComponent } from './batch-job-details.component';
import { DetailsRoutingUrlParts } from './details-routing-url-parts';
import { UnitDetailsComponent } from './unit-details.component';

const routes: Routes = [
  {
    path: `${DetailsRoutingUrlParts.processUnitUrlPart}/:${DetailsRoutingUrlParts.processUnitIdParamName}`,
    component: UnitDetailsComponent,
  },
  {
    path: `${DetailsRoutingUrlParts.batchJobUrlPart}/:${DetailsRoutingUrlParts.batchJobIdParamName}`,
    component: BatchJobDetailsComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class DetailsRoutingModule {}
