import { Routes } from '@angular/router';
import { provideEffects } from '@ngrx/effects';
import { provideState } from '@ngrx/store';
import { DashboardComponent } from './dashboard.component';
import { DashboardEffects } from './ngrx/dashboard.effects';
import { dashboardSlice } from './ngrx/dashboard.reducer';

export const routes: Routes = [
  {
    path: '',
    component: DashboardComponent,
    providers: [
      provideState(dashboardSlice),
      provideEffects(DashboardEffects),
    ],
  },
];

export default routes;
