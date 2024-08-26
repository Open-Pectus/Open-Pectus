import { effect, Injectable } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { Store } from '@ngrx/store';
import { injectQuery, injectQueryClient } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';
import { ProcessUnitService } from '../api/services/ProcessUnitService';
import { PubSubService } from '../shared/pub-sub.service';
import { UtilMethods } from '../shared/util-methods';
import { DetailsSelectors } from './ngrx/details.selectors';

@Injectable({providedIn: 'root'})
export class DetailsQueriesService {
  constructor(private processUnitService: ProcessUnitService,
              private store: Store,
              private pubSubService: PubSubService) {}

  injectProcessValuesQuery() {
    const engineId = UtilMethods.throwIfEmpty(toSignal(this.store.select(DetailsSelectors.processUnitId)));
    return injectQuery(() => ({
      refetchInterval: 1000,
      queryKey: ['processValues', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getProcessValues(engineId())),
    }));
  }

  injectProcessDiagramQuery() {
    const engineId = UtilMethods.throwIfEmpty(toSignal(this.store.select(DetailsSelectors.processUnitId)));
    return injectQuery(() => ({
      queryKey: ['processDiagram', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getProcessDiagram(engineId())),
    }));
  }

  injectCommandExamplesQuery() {
    const engineId = UtilMethods.throwIfEmpty(toSignal(this.store.select(DetailsSelectors.processUnitId)));
    return injectQuery(() => ({
      queryKey: ['commandExamples', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getCommandExamples(engineId())),
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
      queryFn: () => lastValueFrom(this.processUnitService.getControlState(engineId())),
    }));
  }
}
