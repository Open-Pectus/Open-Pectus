import { createFeatureSelector, createSelector } from '@ngrx/store';
import { AppSelectors } from '../../ngrx/app.selectors';
import { selectRouteParam } from '../../ngrx/router.selectors';
import { DetailsRoutingUrlParts } from '../details-routing-url-parts';
import { detailsSlice, DetailsState } from './details.reducer';

export class DetailsSelectors {
  static selectFeature = createFeatureSelector<DetailsState>(detailsSlice.name);
  static processValues = createSelector(this.selectFeature, state => state.processValues);
  static processDiagram = createSelector(this.selectFeature, state => state.processDiagram);
  static commandExamples = createSelector(this.selectFeature, state => state.commandExamples);
  static controlState = createSelector(this.selectFeature, state => state.controlState);
  static recentRun = createSelector(this.selectFeature, state => state.recentRun);
  static shouldPoll = createSelector(this.selectFeature, state => state.shouldPoll);
  static allProcessValues = createSelector(this.selectFeature, state => state.allProcessValues);
  static processUnitId = selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName);
  static processUnit = createSelector(AppSelectors.processUnits, DetailsSelectors.processUnitId,
    (processUnits, unitId) => {
      return processUnits.find(processUnit => processUnit.id.toString() === unitId);
    });
  static missingRoles = createSelector(this.selectFeature, state => state.missingRoles);
  static otherActiveUsers = createSelector(this.selectFeature, state => state.otherActiveUsers);
}
