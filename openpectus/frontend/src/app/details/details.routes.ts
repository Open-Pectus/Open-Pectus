import { Routes } from '@angular/router';
import { provideEffects } from '@ngrx/effects';
import { provideState } from '@ngrx/store';
import { BatchJobDetailsComponent } from './batch-job-details.component';
import { DetailsRoutingUrlParts } from './details-routing-url-parts';
import { MethodEditorEffects } from './method-editor/ngrx/method-editor.effects';
import { methodEditorSlice } from './method-editor/ngrx/method-editor.reducer';
import { DetailsEffects } from './ngrx/details.effects';
import { detailsSlice } from './ngrx/details.reducer';
import { ProcessPlotEffects } from './process-plot/ngrx/process-plot.effects';
import { processPlotSlice } from './process-plot/ngrx/process-plot.reducer';
import { ProcessValuesEffects } from './process-values/ngrx/process-values.effects';
import { processValuesSlice } from './process-values/ngrx/process-values.reducer';
import { RunLogEffects } from './run-log/ngrx/run-log.effects';
import { runLogSlice } from './run-log/ngrx/run-log.reducer';
import { UnitDetailsComponent } from './unit-details.component';

export const routes: Routes = [
  {
    path: '',
    providers: [
      provideState(detailsSlice), provideEffects(DetailsEffects),
      provideState(methodEditorSlice), provideEffects(MethodEditorEffects),
      provideState(processPlotSlice), provideEffects(ProcessPlotEffects),
      provideState(processValuesSlice), provideEffects(ProcessValuesEffects),
      provideState(runLogSlice), provideEffects(RunLogEffects),
    ],
    children: [
      {
        path: `${DetailsRoutingUrlParts.processUnitUrlPart}/:${DetailsRoutingUrlParts.processUnitIdParamName}`,
        component: UnitDetailsComponent,
      },
      {
        path: `${DetailsRoutingUrlParts.batchJobUrlPart}/:${DetailsRoutingUrlParts.batchJobIdParamName}`,
        component: BatchJobDetailsComponent,
      },
    ],
  },
];

export default routes;
