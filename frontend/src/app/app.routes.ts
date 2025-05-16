import { Routes } from '@angular/router';
import { AuthCallbackComponent } from './auth/auth-callback.component';
import { authGuard } from './auth/auth.guard';

export const dashboardUrlPart = 'dashboard';
export const detailsUrlPart = 'details';
export const authCallbackUrlPart = 'auth-callback';

export const APP_ROUTES: Routes = [
  {
    path: dashboardUrlPart,
    loadChildren: () => import('./dashboard/dashboard.routes'),
    canActivate: [authGuard],
  },
  {
    path: detailsUrlPart,
    loadChildren: () => import('./details/details.routes'),
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

export default APP_ROUTES;
