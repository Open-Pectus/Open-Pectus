import { effect, Injectable, Injector } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { Store } from '@ngrx/store';
import { injectQuery, injectQueryClient } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';
import { ProcessUnitService, RecentRunsService } from '../api';
import { PubSubService } from '../shared/pub-sub.service';
import { UtilMethods } from '../shared/util-methods';
import { DetailsSelectors } from './ngrx/details.selectors';

@Injectable({providedIn: 'root'})
export class DetailsQueriesService {
  constructor(private processUnitService: ProcessUnitService,
              private store: Store,
              private pubSubService: PubSubService,
              private recentRunsService: RecentRunsService) {}

  injectProcessValuesQuery(injector?: Injector) {
    const engineId = UtilMethods.throwIfEmpty(toSignal(this.store.select(DetailsSelectors.processUnitId), {injector}));
    return injectQuery(() => ({
      refetchInterval: 1000,
      queryKey: ['processValues', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getProcessValues({engineId: engineId()})),
    }), injector);
  }

  injectProcessDiagramQuery() {
    const engineId = UtilMethods.throwIfEmpty(toSignal(this.store.select(DetailsSelectors.processUnitId)));
    return injectQuery(() => ({
      queryKey: ['processDiagram', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getProcessDiagram({unitId: engineId()})),
    }));
  }

  injectCommandExamplesQuery() {
    const engineId = UtilMethods.throwIfEmpty(toSignal(this.store.select(DetailsSelectors.processUnitId)));
    return injectQuery(() => ({
      queryKey: ['commandExamples', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getCommandExamples({unitId: engineId()})),
    }));
  }

  injectControlStateQuery() {
    const engineId = UtilMethods.throwIfEmpty(toSignal(this.store.select(DetailsSelectors.processUnitId)));
    const queryClient = injectQueryClient();
    const controlStateKey = 'controlState';
    effect((onCleanup) => {
      const subscription = this.pubSubService.subscribeControlState(engineId())
        .subscribe(() => void queryClient.invalidateQueries({queryKey: [controlStateKey]}));
      onCleanup(() => subscription.unsubscribe());
    });

    return injectQuery(() => ({
      queryKey: [controlStateKey, engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getControlState({unitId: engineId()})),
    }));
  }

  injectRecentRunQuery() {
    const recentRunId = UtilMethods.throwIfEmpty(toSignal(this.store.select(DetailsSelectors.recentRunId)));
    return injectQuery(() => ({
      queryKey: ['recentRuns', recentRunId()],
      queryFn: () => lastValueFrom(this.recentRunsService.getRecentRun({runId: recentRunId()})),
    }));
  }
}
