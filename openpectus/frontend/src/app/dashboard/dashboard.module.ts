import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardComponent } from './dashboard.component';
import { DashboardRoutingModule } from './dashboard-routing.module';
import { StoreModule } from '@ngrx/store';
import { dashboardFeatureKey, dashboardReducer } from '../ngrx/dashboard.reducer';
import { EffectsModule } from '@ngrx/effects';
import { DashboardEffects } from '../ngrx/dashboard.effects';
import { DashboardProcessUnitsComponent } from './process-units/dashboard-process-units.component';
import { ProcessUnitCardComponent } from './process-units/process-unit-card.component';
import { PushModule } from '@ngrx/component';
import { SharedModule } from '../shared/shared.module';
import { RecentBatchJobsComponent } from './recent-batch-jobs/recent-batch-jobs.component';


@NgModule({
  declarations: [
    DashboardComponent,
    DashboardProcessUnitsComponent,
    ProcessUnitCardComponent,
    RecentBatchJobsComponent,
  ],
  imports: [
    CommonModule,
    DashboardRoutingModule,
    StoreModule.forFeature(dashboardFeatureKey, dashboardReducer),
    EffectsModule.forFeature([DashboardEffects]),
    PushModule,
    SharedModule,
  ],
})
export class DashboardModule {}
