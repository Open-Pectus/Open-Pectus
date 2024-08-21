import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { PushPipe } from '@ngrx/component';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { CollapsibleElementComponent } from '../shared/collapsible-element.component';
import { ProcessValuePipe } from '../shared/pipes/process-value.pipe';
import { DetailQueries } from './detail.queries';

@Component({
  selector: 'app-process-diagram',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    CollapsibleElementComponent,
    NgIf,
    PushPipe,
  ],
  styles: [
    ':host ::ng-deep svg { height: 100%; width: 100% }',
  ],
  template: `
    <app-collapsible-element [name]="'Process Diagram'" [heightResizable]="true" [contentHeight]="400"
                             (collapseStateChanged)="collapsed = $event" [codiconName]="'codicon-circuit-board'">
      <div class="flex justify-center h-full" content *ngIf="!collapsed">
        <div class="m-auto" *ngIf="processDiagramQuery.data()?.svg === ''">No diagram available</div>
        <!--        <div class="bg-white rounded-sm p-2" [innerHTML]="diagramWithValues | ngrxPush"></div>-->
      </div>
    </app-collapsible-element>
  `,
})
export class ProcessDiagramComponent {
  engineId = input.required<string>();
  processValuesQuery = injectQuery(() => DetailQueries.processValues(this.engineId));
  processDiagramQuery = injectQuery(() => DetailQueries.processDiagram(this.engineId));
  // diagramWithValues = combineLatest([toObservable(this.processDiagramQuery.data), toObservable(this.processValuesQuery.data)]).pipe(
  //   map(([processDiagram, processValues]) => {
  //     return processDiagram?.svg?.replaceAll(/{{(?<inCurlyBraces>[^}]+)}}/g, (match, inCurlyBraces: string) => {
  //       const withoutSvgTags = inCurlyBraces.replaceAll(/<.+>/g, '').trim();
  //       const isJustValue = withoutSvgTags.toLowerCase().endsWith('.pv');
  //       const isJustUnit = withoutSvgTags.toLowerCase().endsWith('.unit');
  //       const withoutDotNotation = withoutSvgTags.substring(0, withoutSvgTags.lastIndexOf('.'));
  //       const processValueName = (isJustValue || isJustUnit) ? withoutDotNotation : withoutSvgTags;
  //
  //       const matchingProcessValue = processValues?.find(processValue => processValue.name === processValueName);
  //       if(matchingProcessValue === undefined) return '';
  //
  //       const formattedProcessValue = this.processValuePipe.transform(matchingProcessValue) ?? '';
  //       const indexOfSpace = formattedProcessValue.indexOf(' ');
  //       if(isJustValue) return formattedProcessValue.substring(0, indexOfSpace);
  //       if(isJustUnit) return formattedProcessValue.substring(indexOfSpace + 1);
  //       return formattedProcessValue;
  //     }) ?? '';
  //   }),
  //   map(processDiagramString => this.domSanitizer.bypassSecurityTrustHtml(processDiagramString)),
  // );
  protected collapsed = false;

  constructor(private domSanitizer: DomSanitizer,
              private processValuePipe: ProcessValuePipe) {}
}
