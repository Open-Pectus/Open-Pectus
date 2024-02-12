import { Routes } from '@angular/router';
import { provideEffects } from '@ngrx/effects';
import { provideState } from '@ngrx/store';
import { DetailsRoutingUrlParts } from './details-routing-url-parts';
import { ErrorLogEffects } from './error-log/ngrx/error-log.effects';
import { errorLogSlice } from './error-log/ngrx/error-log.reducer';
import { MethodEditorEffects } from './method-editor/ngrx/method-editor.effects';
import { methodEditorSlice } from './method-editor/ngrx/method-editor.reducer';
import { DetailsEffects } from './ngrx/details.effects';
import { detailsSlice } from './ngrx/details.reducer';
import { ProcessPlotEffects } from './process-plot/ngrx/process-plot.effects';
import { processPlotSlice } from './process-plot/ngrx/process-plot.reducer';
import { ProcessValuesEffects } from './process-values/ngrx/process-values.effects';
import { processValuesSlice } from './process-values/ngrx/process-values.reducer';
import { RecentRunDetailsComponent } from './recent-run-details.component';
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
      provideState(errorLogSlice), provideEffects(ErrorLogEffects),
    ],
    children: [
      {
        path: `${DetailsRoutingUrlParts.processUnitUrlPart}/:${DetailsRoutingUrlParts.processUnitIdParamName}`,
        component: UnitDetailsComponent,
      },
      {
        path: `${DetailsRoutingUrlParts.recentRunUrlPart}/:${DetailsRoutingUrlParts.recentRunIdParamName}`,
        component: RecentRunDetailsComponent,
      },
    ],
  },
];

export default routes;
