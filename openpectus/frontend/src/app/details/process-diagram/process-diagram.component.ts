import { DecimalPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { Store } from '@ngrx/store';
import { combineLatest, map } from 'rxjs';
import { DetailsActions } from '../ngrx/details.actions';
import { DetailsSelectors } from '../ngrx/details.selectors';

@Component({
  selector: 'app-process-diagram',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex flex-col bg-sky-700 p-1.5 rounded-md shadow-lg">
      <span class="text-2xl font-bold text-gray-100 pb-2 m-2">Process Diagram</span>
      <div class="bg-white rounded-sm p-2" [innerHTML]="diagramWithValues | ngrxPush">
      </div>
    </div>
  `,
})
export class ProcessDiagramComponent implements OnInit {
  processDiagram = this.store.select(DetailsSelectors.processDiagram);
  processValues = this.store.select(DetailsSelectors.processValues);

  diagramWithValues = combineLatest([this.processDiagram, this.processValues]).pipe(
    map(([processDiagram, processValues]) => {
      return processDiagram?.svg?.replaceAll(/{{(?<processValueName>[^}]+)}}/g, (match, processValueName) => {
        const matchingProcessValue = processValues.find(processValue => processValue.name === processValueName.trim());
        if(matchingProcessValue === undefined) return '';
        return `${this.numberPipe.transform(matchingProcessValue.value, '1.2-2')} ${matchingProcessValue.value_unit}`;
      }) ?? '';
    }),
    map(processDiagramString => this.domSanitizer.bypassSecurityTrustHtml(processDiagramString)),
  );

  constructor(private store: Store,
              private domSanitizer: DomSanitizer,
              private numberPipe: DecimalPipe) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.processDiagramInitialized());
  }
}
