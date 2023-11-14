import { Injectable } from '@angular/core';
import { PubSubRxjsClient } from '../../fastapi_websocket/pub-sub-rxjs-client';

@Injectable({
  providedIn: 'root',
})
export class PubSubService {
  private client = new PubSubRxjsClient({uri: `ws://${window.location.host}/api/frontend-pubsub`});

  subscribeRunLog(unitId: string) {
    return this.client.forTopic(`${unitId}/run-log`);
  }

  subscribeMethod(unitId: string) {
    return this.client.forTopic(`${unitId}/method`);
  }

  subscribeControlState(unitId: string) {
    return this.client.forTopic(`${unitId}/control-state`);
  }
}
