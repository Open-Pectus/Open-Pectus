import { Injectable } from '@angular/core';
import { Store } from '@ngrx/store';
import { PubSubRxjsClient } from '../../fastapi_websocket/pub-sub-rxjs-client';
import { PubSubTopic } from '../api';
import { AppActions } from '../ngrx/app.actions';

@Injectable({
  providedIn: 'root',
})
export class PubSubService {
  private readonly pubSubTopics: Record<PubSubTopic, PubSubTopic> = {
    process_units: 'process_units',
    control_state: 'control_state',
    error_log: 'error_log',
    method: 'method',
    method_state: 'method_state',
    run_log: 'run_log',
    active_users: 'active_users',
  };
  private client = new PubSubRxjsClient({
    uri: `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/api/frontend-pubsub`,
    imitatePublishOnReconnect: true,
    onDisconnect: () => this.store.dispatch(AppActions.websocketDisconnected()),
    onReconnect: () => this.store.dispatch(AppActions.websocketReconnected()),
  });

  constructor(private store: Store) {}

  subscribeProcessUnits() {
    return this.client.forTopic(this.pubSubTopics.process_units);
  }

  subscribeRunLog(unitId: string) {
    return this.client.forTopic(`${unitId}/${this.pubSubTopics.run_log}`);
  }

  subscribeMethod(unitId: string) {
    return this.client.forTopic(`${unitId}/${this.pubSubTopics.method}`);
  }

  subscribeMethodState(unitId: string) {
    return this.client.forTopic(`${unitId}/${this.pubSubTopics.method_state}`);
  }

  subscribeControlState(unitId: string) {
    return this.client.forTopic(`${unitId}/${this.pubSubTopics.control_state}`);
  }

  subscribeErrorLog(unitId: string) {
    return this.client.forTopic(`${unitId}/${this.pubSubTopics.error_log}`);
  }

  subscribeActiveUsers(unitId: string) {
    return this.client.forTopic(`${unitId}/${this.pubSubTopics.active_users}`);
  }
}
