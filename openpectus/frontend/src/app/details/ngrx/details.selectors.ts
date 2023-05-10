import { createFeatureSelector, createSelector } from '@ngrx/store';
import { AppSelectors } from '../../ngrx/app.selectors';
import { selectRouteParam } from '../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../details-routing-url-parts';
import { detailsFeatureKey, DetailsState } from './details.reducer';

export class DetailsSelectors {
  static selectFeature = createFeatureSelector<DetailsState>(detailsFeatureKey);
  static methodEditorIsDirty = createSelector(this.selectFeature, state => state.methodEditorIsDirty);
  static methodEditorContent = createSelector(this.selectFeature, state => state.methodEditorContent);
  static processValues = createSelector(this.selectFeature, state => state.processValues);
  static processUnit = createSelector(AppSelectors.processUnits, selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName),
    (processUnits, unitId) => {
      return processUnits.find(processUnit => processUnit.id.toString() === unitId);
    });
  static processDiagram = createSelector(this.selectFeature, state => state.processDiagram);
  static shouldPollProcessValues = createSelector(this.selectFeature, state => state.shouldPollProcessValues);
}
