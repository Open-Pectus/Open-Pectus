import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { TestWebsocketService } from '../fastapi_websocket/test-websocket.service';
import { AppActions } from './ngrx/app.actions';

@Component({
  selector: 'app-root',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <app-top-bar></app-top-bar>
    <router-outlet></router-outlet>
  `,
})
export class AppComponent implements OnInit {
  constructor(private store: Store,
              private testWebsocketService: TestWebsocketService, // only to get it constructed, so it can run its test. TODO: remove this once pubsub is in actual use.
              private oidcSecurityService: OidcSecurityService,
  ) {}

  ngOnInit() {
    this.oidcSecurityService.checkAuth().subscribe(
      (loginResponse) => {
        console.log('callback authenticated', loginResponse);
      },
    );

    this.store.dispatch(AppActions.pageInitialized());
  }
}
