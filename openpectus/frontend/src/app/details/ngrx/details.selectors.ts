import { createFeatureSelector, createSelector } from '@ngrx/store';
import { AppSelectors } from '../../ngrx/app.selectors';
import { selectRouteParam } from '../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../details-routing-url-parts';
import { detailsSlice, DetailsState } from './details.reducer';

export class DetailsSelectors {
  static selectFeature = createFeatureSelector<DetailsState>(detailsSlice.name);
  static allProcessValues = createSelector(this.selectFeature, state => state.allProcessValues);
  static processUnitId = selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName);
  static recentRunId = selectRouteParam(DetailsRoutingUrlParts.recentRunIdParamName);
  static processUnit = createSelector(AppSelectors.processUnits, DetailsSelectors.processUnitId,
    (processUnits, unitId) => {
      return processUnits.find(processUnit => processUnit.id === unitId);
    },
  );
}
