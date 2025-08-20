import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { tap } from 'rxjs/operators';

export const httpErrorInterceptor: HttpInterceptorFn = (req, next) => {
  const toastr = inject(ToastrService);
  return next(req).pipe(tap({
    error: (error: HttpErrorResponse) => {
      // some users don't have a profile picture and trying to fetch one will give 404. We don't want to bother the user with an error message in this case
      if(error.url?.startsWith('https://graph.microsoft.com/')
         && error.url?.endsWith('/photos/48x48/$value')
         && error.status === 404) {
        return;
      }

      const endpoint = error.url?.split('/').at(-1);
      toastr.error(error.error.message, `HTTP Error "${error.statusText}" on endpoint "${endpoint}"`, {
        timeOut: 1000 * 30,
        extendedTimeOut: 1000 * 60 * 2,
      });
    },
  }));
};
