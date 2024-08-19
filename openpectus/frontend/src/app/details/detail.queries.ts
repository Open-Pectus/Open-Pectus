import { Injectable, Signal } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';
import { ProcessUnitService } from '../api/services/ProcessUnitService';

@Injectable({
  providedIn: 'root',
})
export class DetailQueries {
  constructor(private processUnitService: ProcessUnitService) {}

  processValues(engineId: Signal<string | undefined>) {
    return injectQuery(() => ({
      refetchInterval: 1000,
      queryKey: ['processValues', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getProcessValues(engineId()!)),
      enabled: () => engineId() !== undefined,
    }));
  }

  processDiagram(engineId: Signal<string | undefined>) {
    return injectQuery(() => ({
      queryKey: ['processDiagram', engineId()],
      queryFn: () => lastValueFrom(this.processUnitService.getProcessDiagram(engineId()!)),
      enabled: () => engineId() !== undefined,
    }));
  }
}
