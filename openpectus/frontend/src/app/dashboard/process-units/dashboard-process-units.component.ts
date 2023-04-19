import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { DashboardSelectors } from '../../ngrx/dashboard.selectors';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard-process-units',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex">
      <app-process-unit-card *ngFor="let processUnit of (processUnits | ngrxPush)" [processUnit]="processUnit"
                             class="w-80"
                             (click)="onCardClick(processUnit.id)"></app-process-unit-card>
    </div>
  `,
})
export class DashboardProcessUnitsComponent {
  processUnits = this.store.select(DashboardSelectors.processUnits);

  constructor(private store: Store, private router: Router) {}

  onCardClick(id: number) {
    this.router.navigate(['details', 'unit', id]).then();
  }
}
