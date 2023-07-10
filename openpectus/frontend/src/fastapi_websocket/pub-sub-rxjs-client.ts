import { Observable } from 'rxjs';
import { PubSubCallback, PubSubClient, PubSubPromiseClientConfig } from './pub-sub-client';

export class PubSubRxjsClient {
  private promiseClient: PubSubClient;

  constructor(config: PubSubPromiseClientConfig) {
    this.promiseClient = new PubSubClient(config);
  }

  forTopic(topic: string): Observable<Parameters<PubSubCallback>[0]> {
    return new Observable(subscriber => {
      this.promiseClient.subscribe(topic, subscriber.next.bind(subscriber)).catch(subscriber.error);
      return {unsubscribe: () => this.promiseClient.unsubscribe(topic)};
    });
  }

  forTopics(topics: string[]): Observable<Parameters<PubSubCallback>[0]> {
    return new Observable(subscriber => {
      this.promiseClient.subscribeMany(topics, subscriber.next.bind(subscriber)).catch(subscriber.error);
      return {unsubscribe: () => this.promiseClient.unsubscribeMany(topics)};
    });
  }
}
