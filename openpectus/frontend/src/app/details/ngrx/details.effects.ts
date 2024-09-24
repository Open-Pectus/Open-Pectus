import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { map, mergeMap, of, switchMap } from 'rxjs';
import { ProcessUnitService, RecentRunsService } from '../../api';
import { DetailsActions } from './details.actions';
import { DetailsSelectors } from './details.selectors';

// noinspection JSUnusedGlobalSymbols
@Injectable()
export class DetailsEffects {
  executeUnitControlCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.processUnitCommandButtonClicked),
    concatLatestFrom(() => this.store.select(DetailsSelectors.processUnitId)),
    mergeMap(([{command}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.executeCommand({unitId, requestBody: {command, source: 'unit_button'}});
    }),
  ), {dispatch: false});

  executeManuallyEnteredCommandWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.commandsComponentExecuteClicked),
    concatLatestFrom(() => this.store.select(DetailsSelectors.processUnitId)),
    switchMap(([{command}, unitId]) => {
      if(unitId === undefined) return of();
      return this.processUnitService.executeCommand({unitId, requestBody: {...command}});
    }),
  ), {dispatch: false});

  downloadRecentRunCsvWhenButtonClicked = createEffect(() => this.actions.pipe(
    ofType(DetailsActions.recentRunDownloadCsvButtonClicked),
    switchMap(({recentRunId}) => {
      return this.recentRunsService.getRecentRunCsvJson({runId: recentRunId}).pipe(
        map(RecentRunCsv => {
          const link = document.createElement('a');
          link.download = RecentRunCsv.filename;
          link.href = URL.createObjectURL(new Blob([RecentRunCsv.csv_content]));
          link.click();
        }),
      );
    }),
  ), {dispatch: false});

  constructor(private actions: Actions,
              private store: Store,
              private processUnitService: ProcessUnitService,
              private recentRunsService: RecentRunsService) {}
}
