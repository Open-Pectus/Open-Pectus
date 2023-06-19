import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { Store } from '@ngrx/store';
import { combineLatest, map } from 'rxjs';
import { ProcessValuePipe } from '../shared/pipes/process-value.pipe';
import { DetailsActions } from './ngrx/details.actions';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-process-diagram',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Process Diagram'" [heightResizable]="true" [contentHeight]="400">
      <div class="flex justify-center h-full" content>
        <div class="m-auto" *ngIf="(processDiagram | ngrxPush)?.svg === ''">No diagram available</div>
        <div class="bg-white rounded-sm p-2" [innerHTML]="diagramWithValues | ngrxPush"></div>
      </div>
    </app-collapsible-element>
  `,
  styles: [
    ':host ::ng-deep svg { height: 100%; width: 100% }',
  ],
})
export class ProcessDiagramComponent implements OnInit {
  processDiagram = this.store.select(DetailsSelectors.processDiagram);
  processValues = this.store.select(DetailsSelectors.processValues);

  diagramWithValues = combineLatest([this.processDiagram, this.processValues]).pipe(
    map(([processDiagram, processValues]) => {
      return processDiagram?.svg?.replaceAll(/{{(?<inCurlyBraces>[^}]+)}}/g, (match, inCurlyBraces: string) => {
        const withoutSvgTags = inCurlyBraces.replaceAll(/<.+>/g, '').trim();
        const isJustValue = withoutSvgTags.toLowerCase().endsWith('.pv');
        const isJustUnit = withoutSvgTags.toLowerCase().endsWith('.unit');
        const withoutDotNotation = withoutSvgTags.substring(0, withoutSvgTags.lastIndexOf('.'));
        const processValueName = (isJustValue || isJustUnit) ? withoutDotNotation : withoutSvgTags;

        const matchingProcessValue = processValues.find(processValue => processValue.name === processValueName);
        if(matchingProcessValue === undefined) return '';

        const formattedProcessValue = this.processValuePipe.transform(matchingProcessValue) ?? '';
        const indexOfSpace = formattedProcessValue.indexOf(' ');
        if(isJustValue) return formattedProcessValue.substring(0, indexOfSpace);
        if(isJustUnit) return formattedProcessValue.substring(indexOfSpace + 1);
        return formattedProcessValue;
      }) ?? '';
    }),
    map(processDiagramString => this.domSanitizer.bypassSecurityTrustHtml(processDiagramString)),
  );

  constructor(private store: Store,
              private domSanitizer: DomSanitizer,
              private processValuePipe: ProcessValuePipe) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.processDiagramInitialized());
  }
}
