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
    <app-collapsible-element [name]="'Process Diagram'">
      <div class="bg-white rounded-sm p-2" [innerHTML]="diagramWithValues | ngrxPush" content></div>
    </app-collapsible-element>
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
