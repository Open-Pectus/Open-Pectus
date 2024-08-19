import { inject, Injectable } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';
import { ProcessUnitService } from '../api/services/ProcessUnitService';
import { DetailsRoutingUrlParts } from './details-routing-url-parts';

@Injectable()
export class DetailQueries {

  static processValues() {
    const processUnitService = inject(ProcessUnitService);
    const engineId = inject(ActivatedRoute).snapshot.paramMap.get(DetailsRoutingUrlParts.processUnitIdParamName);
    if(engineId === null) throw Error(`Missing route param ${DetailsRoutingUrlParts.processUnitIdParamName} in processValues query`);
    return injectQuery(() => ({
      queryKey: ['processValues', engineId],
      queryFn: () => lastValueFrom(processUnitService.getProcessValues(engineId)),
    }));
  }

  static processDiagram() {
    const processUnitService = inject(ProcessUnitService);
    const engineId = inject(ActivatedRoute).snapshot.paramMap.get(DetailsRoutingUrlParts.processUnitIdParamName);
    if(engineId === null) throw Error(`Missing route param ${DetailsRoutingUrlParts.processUnitIdParamName} in processValues query`);
    return injectQuery(() => ({
      queryKey: ['processDiagram', engineId],
      queryFn: () => lastValueFrom(processUnitService.getProcessDiagram(engineId)),
    }));
  }
}
