import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Store } from '@ngrx/store';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { TestWebsocketService } from '../fastapi_websocket/test-websocket.service';
import { AppActions } from './ngrx/app.actions';
import { TopBarComponent } from './top-bar.component';

@Component({
  selector: 'app-root',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [TopBarComponent, RouterOutlet],
  template: `
    <app-top-bar></app-top-bar>
    <router-outlet></router-outlet>
  `,
})
export class AppComponent implements OnInit {
  constructor(private store: Store,
              private testWebsocketService: TestWebsocketService, // only to get it constructed, so it can run its test. TODO: remove this once pubsub is in actual use.
              private oidcSecurityService: OidcSecurityService) {}

  ngOnInit() {
    this.oidcSecurityService.checkAuth().subscribe(
      (loginResponse) => {
        this.store.dispatch(AppActions.finishedAuthentication({isAuthenticated: loginResponse.isAuthenticated}));
      },
    );

    this.oidcSecurityService.userData$.subscribe(userData => {
      if(userData.userData === null) return;
      this.store.dispatch(AppActions.userDataLoaded(userData));
    });

    this.store.dispatch(AppActions.pageInitialized());
  }
}
