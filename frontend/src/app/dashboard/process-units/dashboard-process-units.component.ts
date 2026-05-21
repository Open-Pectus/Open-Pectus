import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { detailsUrlPart } from '../../app.routes';
import { DetailsRoutingUrlParts } from '../../details/details-routing-url-parts';
import { AppSelectors } from '../../ngrx/app.selectors';
import { ProcessUnitCardComponent } from './process-unit-card.component';

@Component({
  selector: 'app-dashboard-process-units',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ProcessUnitCardComponent],
  template: `
    <div class="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      @for (processUnit of processUnits(); track processUnit.id) {
        <app-process-unit-card [processUnit]="processUnit"
                               (click)="onCardClick(processUnit.id)" />
      }
    </div>
    @if (processUnits().length === 0) {
      <div class="text-center">No process units available</div>
    }
  `
})
export class DashboardProcessUnitsComponent {
  private store = inject(Store);
  protected processUnits = this.store.selectSignal(AppSelectors.processUnits);
  private router = inject(Router);

  onCardClick(id: string) {
    this.router.navigate([detailsUrlPart, DetailsRoutingUrlParts.processUnitUrlPart, id]).then();
  }
}
