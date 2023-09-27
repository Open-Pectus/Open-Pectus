/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';

import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

@Injectable({
  providedIn: 'root',
})
export class FrontendPubsubService {

    constructor(public readonly http: HttpClient) {}

    /**
     * Trigger Pubsub
     * @returns any Successful Response
     * @throws ApiError
     */
    public triggerPubsub(): Observable<any> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/api/trigger-pubsub',
        });
    }

}
