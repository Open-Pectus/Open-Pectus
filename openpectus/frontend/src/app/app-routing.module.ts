import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthCallbackComponent } from './auth/auth-callback.component';
import { authGuard } from './auth/auth.guard';

export const dashboardUrlPart = 'dashboard';
export const detailsUrlPart = 'details';
export const authCallbackUrlPart = 'auth-callback';

const routes: Routes = [
  {
    path: dashboardUrlPart,
    loadChildren: () => import('./dashboard/dashboard.module').then(m => m.DashboardModule),
    canActivate: [authGuard],
  },
  {
    path: detailsUrlPart,
    loadChildren: () => import('./details/details.module').then(m => m.DetailsModule),
    canActivate: [authGuard],
  },
  {
    path: authCallbackUrlPart,
    component: AuthCallbackComponent,
  },
  {
    path: '',
    redirectTo: dashboardUrlPart,
    pathMatch: 'full',
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
