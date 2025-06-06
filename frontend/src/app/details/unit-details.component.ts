import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { LetDirective, PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { firstValueFrom, pairwise } from 'rxjs';
import { CommandsComponent } from './commands/commands.component';
import { ErrorLogComponent } from './error-log/error-log.component';
import { MethodEditorComponent } from './method-editor/method-editor.component';
import { MethodEditorSelectors } from './method-editor/ngrx/method-editor.selectors';
import { MissingRolesComponent } from './missing-roles.component';
import { DetailsActions } from './ngrx/details.actions';
import { DetailsSelectors } from './ngrx/details.selectors';
import { ProcessDiagramComponent } from './process-diagram.component';
import { ProcessPlotContainerComponent } from './process-plot/process-plot-container.component';
import { ProcessValuesComponent } from './process-values/process-values.component';
import { RunLogComponent } from './run-log/run-log.component';
import { UnitHeaderComponent } from './unit-header/unit-header.component';
import { VariableRowSpanDirective } from './variable-row-span.directive';

@Component({
  selector: 'app-unit-details',
  changeDetection: ChangeDetectionStrategy.OnPush,
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
    VariableRowSpanDirective,
    MissingRolesComponent,
  ],
  template: `
    <app-missing-roles>
      @if ((processUnit | ngrxPush)?.state?.state === 'not_online') {
        <span class="absolute-center lg:text-xl font-bold whitespace-nowrap">
          Process Unit "{{ (processUnit | ngrxPush)?.name }}" is offline!
        </span>
      } @else {
        <div class="grid grid-cols-1 2xl:grid-cols-2 w-full lg:px-6 lg:pt-6 pb-8 gap-6 lg:gap-8" *ngrxLet="unitId as unitId">
          <app-unit-header class="mx-2 my-3 lg:m-0"></app-unit-header>
          <app-process-values></app-process-values>
        </div>
        <div class="grid auto-rows-[1px] grid-cols-1 2xl:grid-cols-2 w-full lg:px-6 gap-x-6 lg:gap-x-8" *ngrxLet="unitId as unitId">
          <app-method-editor [unitId]="unitId" appVariableRowSpan></app-method-editor>
          <app-commands appVariableRowSpan></app-commands>
          <app-run-log [unitId]="unitId" appVariableRowSpan></app-run-log>
          <app-process-diagram appVariableRowSpan></app-process-diagram>
        </div>
        <div class="grid grid-cols-1 2xl:grid-cols-2 w-full lg:px-6 lg:pb-6 gap-6 lg:gap-8" *ngrxLet="unitId as unitId">
          <app-process-plot-container class="2xl:col-span-2" [unitId]="unitId"></app-process-plot-container>
          <app-error-log [unitId]="unitId" class="2xl:col-span-2"></app-error-log>
        </div>
      }
    </app-missing-roles>
  `,
})
export class UnitDetailsComponent implements OnInit, OnDestroy {
  public readonly methodIsDirty = this.store.selectSignal(MethodEditorSelectors.isDirty);
  protected readonly unitId = this.store.select(DetailsSelectors.processUnitId);
  protected readonly processUnit = this.store.select(DetailsSelectors.processUnit);

  constructor(private store: Store) {
    this.unitId.pipe(pairwise(), takeUntilDestroyed()).subscribe(([oldUnitId, newUnitId]) => {
      this.store.dispatch(DetailsActions.processUnitNavigatedFrom({oldUnitId, newUnitId}));
    });
  }

  async ngOnInit() {
    const unitId = await firstValueFrom(this.unitId);
    if(unitId === undefined) throw Error('UnitDetailsComponent initialized without a process unit id in url');
    this.store.dispatch(DetailsActions.unitDetailsInitialized({unitId}));
  }

  ngOnDestroy() {
    this.store.dispatch(DetailsActions.unitDetailsDestroyed());
  }
}
