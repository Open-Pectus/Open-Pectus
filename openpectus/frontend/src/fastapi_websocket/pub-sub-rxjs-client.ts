import { Observable } from 'rxjs';
import { PubSubCallbackParameters, PubSubClient, PubSubPromiseClientConfig } from './pub-sub-client';

export class PubSubRxjsClient {
  private promiseClient: PubSubClient;

  constructor(config: PubSubPromiseClientConfig) {
    this.promiseClient = new PubSubClient(config);
  }

  forTopic(topic: string): Observable<PubSubCallbackParameters> {
    return new Observable(subscriber => {
      const callback = subscriber.next.bind(subscriber);
      this.promiseClient.subscribe(topic, callback).catch(subscriber.error);
      return {unsubscribe: () => this.promiseClient.unsubscribe(topic, callback)};
    });
  }

  forTopics(topics: string[]): Observable<PubSubCallbackParameters> {
    return new Observable(subscriber => {
      const callback = subscriber.next.bind(subscriber);
      this.promiseClient.subscribeMany(topics, callback).catch(subscriber.error);
      return {unsubscribe: () => this.promiseClient.unsubscribeMany(topics, callback)};
    });
  }
}
