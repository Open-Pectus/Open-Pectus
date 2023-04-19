import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

export const dashboardUrlPart = 'dashboard';
export const detailsUrlPart = 'details';

const routes: Routes = [
  {
    path: `${dashboardUrlPart}`,
    loadChildren: () => import('./dashboard/dashboard.module').then(m => m.DashboardModule),
  },
  {
    path: `${detailsUrlPart}`,
    loadChildren: () => import('./details/details.module').then(m => m.DetailsModule),
  },
  {
    path: '',
    redirectTo: `${dashboardUrlPart}`,
    pathMatch: 'full',
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
