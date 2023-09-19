import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { take } from 'rxjs';

@Component({
  selector: 'app-auth-callback',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex items-center justify-center absolute h-full w-full">
      Please wait...
    </div>
  `,
})
export class AuthCallbackComponent implements OnInit {
  constructor(private router: Router,
              private oidcSecurityService: OidcSecurityService) {}

  ngOnInit() {
    this.oidcSecurityService.isAuthenticated().pipe(take(1)).subscribe(isAuthenticated => {
      if(isAuthenticated) this.router.navigate(['/']).then();
    });
  }
}
