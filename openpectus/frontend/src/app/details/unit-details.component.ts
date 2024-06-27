import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { LetDirective, PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { firstValueFrom } from 'rxjs';
import { NotOnline } from '../api/models/NotOnline';
import { CommandsComponent } from './commands/commands.component';
import { ErrorLogComponent } from './error-log/error-log.component';
import { MethodEditorComponent } from './method-editor/method-editor.component';
import { DetailsActions } from './ngrx/details.actions';
import { DetailsSelectors } from './ngrx/details.selectors';
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
    ErrorLogComponent,
    PushPipe,
  ],
  template: `
    @if ((processUnit | ngrxPush)?.state?.state !== NotOnline.state.NOT_ONLINE) {
      <div class="grid grid-cols-1 2xl:grid-cols-2 w-full lg:px-6 lg:py-6 gap-6 lg:gap-8" *ngrxLet="unitId as unitId">
        <app-unit-header class="mx-2 my-3 lg:m-0"></app-unit-header>
        <app-process-values></app-process-values>
        <app-method-editor [unitId]="unitId"></app-method-editor>
        <app-commands></app-commands>
        <app-run-log [unitId]="unitId"></app-run-log>
        <app-process-diagram></app-process-diagram>
        <app-process-plot-container class="2xl:col-span-2" [unitId]="unitId"></app-process-plot-container>
        <app-error-log [unitId]="unitId" class="2xl:col-span-2"></app-error-log>
      </div>
    } @else {
      <span class="absolute-center lg:text-xl font-bold whitespace-nowrap">
        Process Unit "{{ (processUnit | ngrxPush)?.name }}" is offline!
      </span>
    }
  `,
})
export class UnitDetailsComponent implements OnInit, OnDestroy {
  protected readonly unitId = this.store.select(DetailsSelectors.processUnitId);
  protected readonly processUnit = this.store.select(DetailsSelectors.processUnit);
  protected readonly NotOnline = NotOnline;

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
