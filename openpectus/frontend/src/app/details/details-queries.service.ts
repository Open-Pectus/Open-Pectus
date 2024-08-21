import { Injectable, Signal } from '@angular/core';
import { queryOptions } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';
import { ProcessUnitService } from '../api/services/ProcessUnitService';

@Injectable({providedIn: 'root'})
export class DetailsQueriesService {
  constructor(private processUnitService: ProcessUnitService) {}

  processValues(engineId: Signal<string>) {
    return queryOptions({
      refetchInterval: 1000,
      queryKey: ['processValues', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getProcessValues(engineId())),
    });
  }

  processDiagram(engineId: Signal<string>) {
    return queryOptions({
      queryKey: ['processDiagram', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getProcessDiagram(engineId())),
    });
  }

  commandExamples(engineId: Signal<string>) {
    return queryOptions({
      queryKey: ['commandExamples', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getCommandExamples(engineId())),
    });
  }

  controlState(engineId: Signal<string>) {
    return queryOptions({
      queryKey: ['controlState', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getControlState(engineId())),
    });
  }
}
