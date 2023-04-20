import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { DashboardSelectors } from '../../ngrx/dashboard.selectors';
import { Router } from '@angular/router';
import { processUnitUrlPart } from '../../details/details-routing.module';
import { detailsUrlPart } from '../../app-routing.module';

@Component({
  selector: 'app-dashboard-process-units',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      <app-process-unit-card *ngFor="let processUnit of (processUnits | ngrxPush)" [processUnit]="processUnit"
                             (click)="onCardClick(processUnit.id)"></app-process-unit-card>
    </div>
  `,
})
export class DashboardProcessUnitsComponent {
  processUnits = this.store.select(DashboardSelectors.processUnits);

  constructor(private store: Store, private router: Router) {}

  onCardClick(id: number) {
    this.router.navigate([detailsUrlPart, processUnitUrlPart, id]).then();
  }
}
