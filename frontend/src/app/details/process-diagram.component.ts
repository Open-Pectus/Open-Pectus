import { NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, OnInit, inject } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { Store } from '@ngrx/store';
import { CollapsibleElementComponent } from '../shared/collapsible-element.component';
import { ProcessValuePipe } from '../shared/pipes/process-value.pipe';
import { DetailsActions } from './ngrx/details.actions';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-process-diagram',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CollapsibleElementComponent,
    NgIf,

  ],
  styles: [
    ':host ::ng-deep svg { height: 100%; width: 100% }',
  ],
  template: `
    <app-collapsible-element [name]="'Process Diagram'" [heightResizable]="true" [contentHeight]="400"
                             (collapseStateChanged)="collapsed = $event" [codiconName]="'codicon-circuit-board'">
      <div class="flex justify-center h-full" content *ngIf="!collapsed">
        <div class="m-auto" *ngIf="processDiagram()?.svg === ''">No diagram available</div>
        <div class="bg-white rounded-sm p-2" [innerHTML]="diagramWithValues()"></div>
      </div>
    </app-collapsible-element>
  `
})
export class ProcessDiagramComponent implements OnInit {
  private store = inject(Store);
  private domSanitizer = inject(DomSanitizer);
  private processValuePipe = inject(ProcessValuePipe);

  processDiagram = this.store.selectSignal(DetailsSelectors.processDiagram);
  processValues = this.store.selectSignal(DetailsSelectors.processValues);
  diagramWithValues = computed(() => {
    const processDiagramString = this.processDiagram()?.svg?.replaceAll(/{{(?<inCurlyBraces>[^}]+)}}/g, (match, inCurlyBraces: string) => {
      const withoutSvgTags = inCurlyBraces.replaceAll(/<.+>/g, '').trim();
      const isJustValue = withoutSvgTags.toLowerCase().endsWith('.pv');
      const isJustUnit = withoutSvgTags.toLowerCase().endsWith('.unit');
      const withoutDotNotation = withoutSvgTags.substring(0, withoutSvgTags.lastIndexOf('.'));
      const processValueName = (isJustValue || isJustUnit) ? withoutDotNotation : withoutSvgTags;

      const matchingProcessValue = this.processValues().find(processValue => processValue.name === processValueName);
      if(matchingProcessValue === undefined) return '';

      const formattedProcessValue = this.processValuePipe.transform(matchingProcessValue) ?? '';
      const indexOfSpace = formattedProcessValue.indexOf(' ');
      if(isJustValue) return formattedProcessValue.substring(0, indexOfSpace);
      if(isJustUnit) return formattedProcessValue.substring(indexOfSpace + 1);
      return formattedProcessValue;
    }) ?? '';
    return this.domSanitizer.bypassSecurityTrustHtml(processDiagramString);
  });
  protected collapsed = false;

  ngOnInit() {
    this.store.dispatch(DetailsActions.processDiagramInitialized());
  }
}
