import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { WebsocketRpcClient } from '../fastapi_websocket/websocket-rpc-client';
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
  constructor(private store: Store) {}

  ngOnInit() {
    this.store.dispatch(AppActions.pageInitialized());

    const rpcClient = new WebsocketRpcClient(`ws://${window.location.host}/ws`, {
      concat(a: string, b: string) {
        return a + b;
      },
    });
    rpcClient.waitForReady().then(() => {
      rpcClient.call('concat', {a: 'first ', b: 'second'}).then(result => console.debug('concat call result:', result));
    });
  }
}
