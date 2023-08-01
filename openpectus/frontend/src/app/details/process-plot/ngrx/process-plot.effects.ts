import { Injectable } from '@angular/core';
import { Actions, concatLatestFrom, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { map, of, switchMap } from 'rxjs';
import { ProcessUnitService } from '../../../api';
import { selectRouteParam } from '../../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../../details-routing-url-parts';
import { ProcessPlotActions } from './process-plot.actions';

@Injectable()
export class ProcessPlotEffects {
  fetchProcessPlotConfigurationOnComponentInitialization = createEffect(() => this.actions.pipe(
    ofType(ProcessPlotActions.processPlotComponentInitialized),
    concatLatestFrom(() => this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName))),
    switchMap(([_, id]) => {
      if(id === undefined) return of();
      return this.processUnitService.getPlotConfiguration(id).pipe(
        map(configuration => ProcessPlotActions.plotConfigurationFetched({configuration})));
    }),
  ));

  constructor(private actions: Actions, private store: Store, private processUnitService: ProcessUnitService) {}
}
