import { RouterModule, Routes } from '@angular/router';
import { NgModule } from '@angular/core';
import { UnitDetailsComponent } from './unit-details.component';
import { BatchJobDetailsComponent } from './batch-job-details.component';

export const processUnitUrlPart = 'process_unit';
export const batchJobUrlPart = 'batch_job';
export const unitIdParamName = 'unit_id';
export const batchJobIdParamName = 'batch_job_id';

const routes: Routes = [
  {
    path: `${processUnitUrlPart}/:${unitIdParamName}`,
    component: UnitDetailsComponent,
  },
  {
    path: `${batchJobUrlPart}/:${batchJobIdParamName}`,
    component: BatchJobDetailsComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class DetailsRoutingModule {}
