import { Injectable } from '@angular/core';
import { PubSubRxjsClient } from '../../fastapi_websocket/pub-sub-rxjs-client';
import { PubSubTopic } from '../api';

@Injectable({
  providedIn: 'root',
})
export class PubSubService {
  private client = new PubSubRxjsClient(
    {uri: `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/api/frontend-pubsub`});

  subscribeProcessUnits() {
    return this.client.forTopic(PubSubTopic.PROCESS_UNITS);
  }

  subscribeRunLog(unitId: string) {
    return this.client.forTopic(`${unitId}/${PubSubTopic.RUN_LOG}`);
  }

  subscribeMethod(unitId: string) {
    return this.client.forTopic(`${unitId}/${PubSubTopic.METHOD}`);
  }

  subscribeControlState(unitId: string) {
    return this.client.forTopic(`${unitId}/${PubSubTopic.CONTROL_STATE}`);
  }

  subscribeErrorLog(unitId: string) {
    return this.client.forTopic(`${unitId}/${PubSubTopic.ERROR_LOG}`);
  }
}
