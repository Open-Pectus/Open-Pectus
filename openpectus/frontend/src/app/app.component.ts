import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
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
  ) {}

  ngOnInit() {
    this.store.dispatch(AppActions.pageInitialized());
  }
}
