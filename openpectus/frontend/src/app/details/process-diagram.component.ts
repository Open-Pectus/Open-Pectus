import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { toObservable } from '@angular/core/rxjs-interop';
import { DomSanitizer } from '@angular/platform-browser';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { combineLatest, map } from 'rxjs';
import { CollapsibleElementComponent } from '../shared/collapsible-element.component';
import { ProcessValuePipe } from '../shared/pipes/process-value.pipe';
import { DetailQueries } from './detail.queries';
import { DetailsActions } from './ngrx/details.actions';

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
        <div class="m-auto" *ngIf="processDiagram.data()?.svg === ''">No diagram available</div>
        <div class="bg-white rounded-sm p-2" [innerHTML]="diagramWithValues | ngrxPush"></div>
      </div>
    </app-collapsible-element>
  `,
})
export class ProcessDiagramComponent implements OnInit {
  // engineId = input.required<string>();
  processValues = DetailQueries.processValues();
  processDiagram = DetailQueries.processDiagram();
  // processDiagram = this.store.select(DetailsSelectors.processDiagram);
  // processValues = this.store.select(DetailsSelectors.processValues);
  diagramWithValues = combineLatest([toObservable(this.processDiagram.data), toObservable(this.processValues.data)]).pipe(
    map(([processDiagram, processValues]) => {
      return processDiagram?.svg?.replaceAll(/{{(?<inCurlyBraces>[^}]+)}}/g, (match, inCurlyBraces: string) => {
        const withoutSvgTags = inCurlyBraces.replaceAll(/<.+>/g, '').trim();
        const isJustValue = withoutSvgTags.toLowerCase().endsWith('.pv');
        const isJustUnit = withoutSvgTags.toLowerCase().endsWith('.unit');
        const withoutDotNotation = withoutSvgTags.substring(0, withoutSvgTags.lastIndexOf('.'));
        const processValueName = (isJustValue || isJustUnit) ? withoutDotNotation : withoutSvgTags;

        const matchingProcessValue = processValues?.find(processValue => processValue.name === processValueName);
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
  protected collapsed = false;

  constructor(private store: Store,
              private domSanitizer: DomSanitizer,
              private processValuePipe: ProcessValuePipe) {}

  ngOnInit() {
    this.store.dispatch(DetailsActions.processDiagramInitialized());
  }
}
