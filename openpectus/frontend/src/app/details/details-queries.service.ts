import { effect, Injectable, Signal } from '@angular/core';
import { injectQueryClient, queryOptions, skipToken } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';
import { ProcessUnitService, RecentRunsService } from '../api';
import { PubSubService } from '../shared/pub-sub.service';

@Injectable({providedIn: 'root'})
export class DetailsQueriesService {

  constructor(private processUnitService: ProcessUnitService,
              private pubSubService: PubSubService,
              private recentRunsService: RecentRunsService) {}

  processValuesQuery(engineId: Signal<string | undefined>) {
    const engineIdValue = engineId();
    return queryOptions({
      refetchInterval: 1000,
      queryKey: ['processValues', engineIdValue],
      queryFn: engineIdValue === undefined ? skipToken : () => lastValueFrom(
        this.processUnitService.getProcessValues({engineId: engineIdValue})),
    });
  }

  processDiagramQuery(engineId: Signal<string>) {
    return queryOptions({
      queryKey: ['processDiagram', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getProcessDiagram({unitId: engineId()})),
    });
  }

  commandExamplesQuery(engineId: Signal<string>) {
    return queryOptions({
      queryKey: ['commandExamples', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getCommandExamples({unitId: engineId()})),
    });
  }

  controlStateQuery(engineId: Signal<string>) {
    return queryOptions({
      queryKey: ['controlState', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getControlState({unitId: engineId()})),
    });
  }

  subscribeToControlStateUpdates(engineId: Signal<string>) {
    const queryClient = injectQueryClient();
    effect((onCleanup) => {
      const subscription = this.pubSubService.subscribeControlState(engineId())
        .subscribe(() => void queryClient.invalidateQueries(this.controlStateQuery(engineId)));
      onCleanup(() => subscription.unsubscribe());
    });
  }

  recentRunQuery(recentRunId: Signal<string>) {
    return queryOptions({
      queryKey: ['recentRuns', recentRunId()],
      queryFn: () => lastValueFrom(this.recentRunsService.getRecentRun({runId: recentRunId()})),
    });
  }
}
