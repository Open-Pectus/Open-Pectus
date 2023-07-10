import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { take } from 'rxjs';
import { PubSubClient } from '../fastapi_websocket/pub-sub-client';
import { PubSubRxjsClient } from '../fastapi_websocket/pub-sub-rxjs-client';
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
    // this.testPubSubClient();
    this.testPubSubRxjsClient();
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
    const pubSubClient = new PubSubClient({uri: `ws://${window.location.host}/api/frontend-pubsub`});
    pubSubClient.subscribeMany(['guns', 'germs'], ({topic}) => {
      console.debug(`callback for ${topic}`);
    }).then();

    pubSubClient.subscribe('steel', ({data, topic}) => {
      console.debug(`callback for ${topic} with data`, data);
    }).then();
  }

  private testPubSubRxjsClient() {
    const pubSubRxjsClient = new PubSubRxjsClient({uri: `ws://${window.location.host}/api/frontend-pubsub`});
    pubSubRxjsClient.forTopics(['guns', 'germs', 'steel']).pipe(take(2)).subscribe(({topic}) => {
      console.debug(`callback for ${topic}`);
    });

    pubSubRxjsClient.forTopic('steel').subscribe(({data, topic}) => {
      console.debug(`callback for ${topic} with data`, data);

    });
  }
}
