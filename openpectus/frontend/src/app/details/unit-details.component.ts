import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { LetDirective } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { firstValueFrom } from 'rxjs';
import { selectRouteParam } from '../ngrx/router.selectors';
import { CommandsComponent } from './commands/commands.component';
import { DetailsRoutingUrlParts } from './details-routing-url-parts';
import { ErrorLogComponent } from './error-log.component';
import { MethodEditorComponent } from './method-editor/method-editor.component';
import { DetailsActions } from './ngrx/details.actions';
import { ProcessDiagramComponent } from './process-diagram.component';
import { ProcessPlotContainerComponent } from './process-plot/process-plot-container.component';
import { ProcessValuesComponent } from './process-values/process-values.component';
import { RunLogComponent } from './run-log/run-log.component';
import { UnitHeaderComponent } from './unit-header/unit-header.component';

@Component({
  selector: 'app-unit-details',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [
    LetDirective,
    UnitHeaderComponent,
    ProcessValuesComponent,
    MethodEditorComponent,
    CommandsComponent,
    RunLogComponent,
    ProcessDiagramComponent,
    ProcessPlotContainerComponent,
    ErrorLogComponent,
  ],
  template: `
    <div class="flex justify-center">
      <div class="grid grid-cols-1 2xl:grid-cols-2 w-full lg:px-6 lg:py-8 gap-4 lg:gap-8" *ngrxLet="unitId as unitId">
        <app-unit-header class="mx-2 my-3 lg:m-0"></app-unit-header>
        <app-process-values></app-process-values>
        <app-method-editor [unitId]="unitId"></app-method-editor>
        <app-commands></app-commands>
        <app-run-log [unitId]="unitId"></app-run-log>
        <app-process-diagram></app-process-diagram>
        <app-process-plot-container class="2xl:col-span-2" [unitId]="unitId"></app-process-plot-container>
        <app-error-log class="2xl:col-span-2"></app-error-log>
      </div>
    </div>
  `,
})
export class UnitDetailsComponent implements OnInit, OnDestroy {
  protected unitId = this.store.select(selectRouteParam(DetailsRoutingUrlParts.processUnitIdParamName));

  constructor(private store: Store) {}

  async ngOnInit() {
    const unitId = await firstValueFrom(this.unitId);
    if(unitId === undefined) throw Error('UnitDetailsComponent initialized without a process unit id in url');
    this.store.dispatch(DetailsActions.unitDetailsInitialized({unitId}));
  }

  ngOnDestroy() {
    this.store.dispatch(DetailsActions.unitDetailsDestroyed());
  }
}
