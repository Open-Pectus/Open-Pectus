import { createFeatureSelector, createSelector } from '@ngrx/store';
import { AppSelectors } from '../../ngrx/app.selectors';
import { selectRouteParam } from '../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../details-routing-url-parts';
import { detailsSlice, DetailsState } from './details.reducer';

export class DetailsSelectors {
  static selectFeature = createFeatureSelector<DetailsState>(detailsSlice.name);
  static processValues = createSelector(this.selectFeature, state => state.processValues);
  static processUnit = createSelector(AppSelectors.processUnits, selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName),
    (processUnits, unitId) => {
      return processUnits.find(processUnit => processUnit.id.toString() === unitId);
    });
  static processDiagram = createSelector(this.selectFeature, state => state.processDiagram);
  static shouldPollProcessValues = createSelector(this.selectFeature, state => state.shouldPollProcessValues);
  static commandExamples = createSelector(this.selectFeature, state => state.commandExamples);
}
