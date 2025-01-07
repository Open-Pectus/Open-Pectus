import { NgFor, NgIf } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router } from '@angular/router';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { detailsUrlPart } from '../../app.routes';
import { DetailsRoutingUrlParts } from '../../details/details-routing-url-parts';
import { AppSelectors } from '../../ngrx/app.selectors';
import { ProcessUnitCardComponent } from './process-unit-card.component';

@Component({
    selector: 'app-dashboard-process-units',
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [
        NgFor,
        ProcessUnitCardComponent,
        NgIf,
        PushPipe,
    ],
    template: `
    <div class="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      <app-process-unit-card *ngFor="let processUnit of (processUnits | ngrxPush)" [processUnit]="processUnit"
                             (click)="onCardClick(processUnit.id)"></app-process-unit-card>
    </div>
    <div class="text-center" *ngIf="(processUnits | ngrxPush)?.length === 0">No process units available</div>
  `
})
export class DashboardProcessUnitsComponent {
  processUnits = this.store.select(AppSelectors.processUnits);

  constructor(private store: Store, private router: Router) {}

  onCardClick(id: string) {
    this.router.navigate([detailsUrlPart, DetailsRoutingUrlParts.processUnitUrlPart, id]).then();
  }
}
