/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';

import type { PubSubTopic } from '../models/PubSubTopic';

import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

@Injectable({
  providedIn: 'root',
})
export class FrontendPubsubService {

    constructor(public readonly http: HttpClient) {}

    /**
     * Expose Pubsub Topics
     * This endpoint is just for exposing the topic enum to frontend via autogeneration
     * @param topic 
     * @returns any Successful Response
     * @throws ApiError
     */
    public exposePubsubTopics(
topic: PubSubTopic,
): Observable<any> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/expose-pubsub-topics',
            query: {
                'topic': topic,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Trigger Publish Msw
     * Publish to all topics that start with 'MSW_'
     * @returns any Successful Response
     * @throws ApiError
     */
    public triggerPublishMsw(): Observable<any> {
        return __request(OpenAPI, this.http, {
            method: 'POST',
            url: '/api/trigger-publish-msw',
        });
    }

}
