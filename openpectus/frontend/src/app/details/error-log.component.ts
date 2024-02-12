import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { Defaults } from '../defaults';
import { CollapsibleElementComponent } from '../shared/collapsible-element.component';
import { DetailsSelectors } from './ngrx/details.selectors';

@Component({
  selector: 'app-error-log',
  standalone: true,
  imports: [CommonModule, CollapsibleElementComponent, LetDirective],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-collapsible-element [name]="'Error Log'" [heightResizable]="true" [contentHeight]="400" [codiconName]="'codicon-warning'"
                             (collapseStateChanged)="collapsed = $event" *ngrxLet="errorLog as errorLog">
      <div content class="p-1">
        <p *ngFor="let entry of errorLog.entries">{{ entry.created_time | date:dateFormat }}: {{ entry.message }}</p>
      </div>
    </app-collapsible-element>
  `,
})
export class ErrorLogComponent {
  protected dateFormat = Defaults.dateFormat + '.SSS';
  protected errorLog = this.store.select(DetailsSelectors.errorLog);
  protected collapsed = true;

  constructor(private store: Store) {}
}

