import { inject, Signal } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';
import { ProcessUnitService } from '../api/services/ProcessUnitService';

export class DetailQueries {
  static processValues(engineId: Signal<string | undefined>) {
    const processUnitService = inject(ProcessUnitService);
    return injectQuery(() => ({
      refetchInterval: 1000,
      queryKey: ['processValues', engineId()],
      queryFn: () => lastValueFrom(processUnitService.getProcessValues(engineId()!)),
      enabled: () => engineId() !== undefined,
    }));
  }

  static processDiagram(engineId: Signal<string | undefined>) {
    const processUnitService = inject(ProcessUnitService);
    return injectQuery(() => ({
      queryKey: ['processDiagram', engineId()],
      queryFn: () => lastValueFrom(processUnitService.getProcessDiagram(engineId()!)),
      enabled: () => engineId() !== undefined,
    }));
  }
}
