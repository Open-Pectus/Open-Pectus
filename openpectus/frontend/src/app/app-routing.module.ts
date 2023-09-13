import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AutoLoginPartialRoutesGuard } from 'angular-auth-oidc-client';
import { AuthCallbackComponent } from './auth-callback.component';

export const dashboardUrlPart = 'dashboard';
export const detailsUrlPart = 'details';
export const authCallbackUrlPart = 'auth-callback';

const routes: Routes = [
  {
    path: dashboardUrlPart,
    loadChildren: () => import('./dashboard/dashboard.module').then(m => m.DashboardModule),
    canActivate: [AutoLoginPartialRoutesGuard],
  },
  {
    path: detailsUrlPart,
    loadChildren: () => import('./details/details.module').then(m => m.DetailsModule),
    canActivate: [AutoLoginPartialRoutesGuard],
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
