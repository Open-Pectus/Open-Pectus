import { Injectable } from '@angular/core';
import { take } from 'rxjs';
import { PubSubClient } from '../../fastapi_websocket/pub-sub-client';
import { PubSubRxjsClient } from '../../fastapi_websocket/pub-sub-rxjs-client';
import { WebsocketRpcClient } from '../../fastapi_websocket/websocket-rpc-client';

@Injectable({
  providedIn: 'root',
})
export class TestWebsocketService {

  constructor() {
    // only test one at a time, as they can interfere.
    // this.testRpcClient();
    // this.testPubSubClient();
    this.testPubSubRxjsClient();
  }

  testRpcClient() {
    const rpcClient = new WebsocketRpcClient(`ws://${window.location.host}/ws`, {
      concat(a: string, b: string) {
        return a + b;
      },
    });
    rpcClient.waitForReady().then(() => {
      rpcClient.call('concat', {a: 'first ', b: 'second'}).then(result => console.debug('concat call result:', result));
    });
  }

  testPubSubClient() {
    const pubSubClient = new PubSubClient({uri: `ws://${window.location.host}/api/frontend-pubsub`});
    pubSubClient.subscribeMany(['guns', 'germs'], ({topic}) => {
      console.debug(`callback for ${topic}`);
    }).then();

    pubSubClient.subscribe('steel', ({data, topic}) => {
      console.debug(`callback for ${topic} with data`, data);
    }).then();
  }

  testPubSubRxjsClient() {
    const pubSubRxjsClient = new PubSubRxjsClient({uri: `ws://${window.location.host}/api/frontend-pubsub`});
    pubSubRxjsClient.forTopics(['guns', 'germs', 'steel']).pipe(take(2)).subscribe(({topic}) => {
      console.debug(`callback for ${topic}`);
    });

    pubSubRxjsClient.forTopic('steel').subscribe(({data, topic}) => {
      console.debug(`callback for ${topic} with data`, data);
    });
  }
}
