import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { PushModule } from '@ngrx/component';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';
import { SharedModule } from '../shared/shared.module';
import { DashboardRoutingModule } from './dashboard-routing.module';
import { DashboardComponent } from './dashboard.component';
import { DashboardEffects } from './ngrx/dashboard.effects';
import { dashboardFeatureKey, dashboardReducer } from './ngrx/dashboard.reducer';
import { DashboardProcessUnitsComponent } from './process-units/dashboard-process-units.component';
import { ProcessUnitCardComponent } from './process-units/process-unit-card.component';
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
