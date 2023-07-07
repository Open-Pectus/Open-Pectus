import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { PubSubClient } from '../fastapi_websocket/pub-sub-client';
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

    // this.testRpcClient();
    this.testPubSubClient();
  }

  private testRpcClient() {
    const rpcClient = new WebsocketRpcClient(`ws://${window.location.host}/ws`, {
      concat(a: string, b: string) {
        return a + b;
      },
    });
    rpcClient.waitForReady().then(() => {
      rpcClient.call('concat', {a: 'first ', b: 'second'}).then(result => console.debug('concat call result:', result));
    });
  }

  private testPubSubClient() {
    const pubSubClient = new PubSubClient(['guns', 'germs'], (data, topic) => {
      console.debug('callback for', topic);
    });

    pubSubClient.subscribe('steel', (data, topic) => {
      console.debug(`callback for ${topic} with data`, data);
    });
  }
}
