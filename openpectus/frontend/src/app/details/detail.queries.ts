import { inject, Signal } from '@angular/core';
import { queryOptions } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';
import { ProcessUnitService } from '../api/services/ProcessUnitService';

export class DetailQueries {
  static processValues(engineId: Signal<string>) {
    const processUnitService = inject(ProcessUnitService);
    return queryOptions({
      refetchInterval: 1000,
      queryKey: ['processValues', engineId()],
      queryFn: () => lastValueFrom(processUnitService.getProcessValues(engineId())),
    });
  }

  static processDiagram(engineId: Signal<string>) {
    const processUnitService = inject(ProcessUnitService);
    return queryOptions({
      queryKey: ['processDiagram', engineId()],
      queryFn: () => lastValueFrom(processUnitService.getProcessDiagram(engineId())),
    });
  }

  static commandExamples(engineId: Signal<string>) {
    const processUnitService = inject(ProcessUnitService);
    return queryOptions({
      queryKey: ['commandExamples', engineId()],
      queryFn: () => lastValueFrom(processUnitService.getCommandExamples(engineId())),
    });
  }
}
