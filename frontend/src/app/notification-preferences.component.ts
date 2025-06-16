import { TitleCasePipe } from '@angular/common';
import { AfterViewInit, ChangeDetectionStrategy, ChangeDetectorRef, Component, ElementRef, ViewChild } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SwPush } from '@angular/service-worker';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { firstValueFrom, map, take } from 'rxjs';
import { NotificationScope, NotificationTopic, WebPushNotificationPreferences, WebpushService, WebPushSubscription } from './api';
import { detailsUrlPart } from './app.routes';
import { DetailsRoutingUrlParts } from './details/details-routing-url-parts';
import { AppSelectors } from './ngrx/app.selectors';

@Component({
  selector: 'app-notification-preferences',
  imports: [ReactiveFormsModule, PushPipe, TitleCasePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button #bell class="codicon codicon-bell !text-xl" (click)="onBellClick()"></button>

    <div popover #popover class="text-black bg-white border-slate-400 p-2 border-2 rounded-lg m-0"
         [style.top.px]="bellPosition.bottom" [style.left.px]="bellPosition.right - popoverWidth" [style.width.px]="popoverWidth">
      <label><input type="checkbox" [checked]="hasSubscription | ngrxPush"
                    (change)="onEnabledChanged($event)"> Notifications enabled for this device</label>
      <form [formGroup]="formGroup">
        <div class="flex flex-col">
          <h1 class="font-bold mt-2">Scopes:</h1>
          <label><input type="radio" [value]="notificationScopes.process_units_i_have_access_to"
                        [formControlName]="scopeControlName"> Process Units I have access to</label>
          <label><input type="radio"
                        [value]="notificationScopes.process_units_with_runs_ive_contributed_to"
                        [formControlName]="scopeControlName"> Process Units with runs I've contributed to</label>
          <label><input type="radio" [value]="notificationScopes.specific_process_units" #specific
                        [formControlName]="scopeControlName"> Specific Process Units:</label>
          @if (specificProcessUnitsSelected) {
            <select multiple [formControlName]="processUnitsControlName">
              @for (processUnit of processUnits(); track processUnit.id) {
                <option [value]="processUnit.id">{{ processUnit.name }}</option>
              }
            </select>
          }

          <h1 class="font-bold mt-2">Topics:</h1>
          <select multiple [formControlName]="topicsControlName">
            @for (optionValue of Object.values(notificationTopics); track optionValue) {
              <option [value]="optionValue">{{ optionValue.replace('_', ' ') | titlecase }}</option>
            }
          </select>
        </div>
      </form>
      <button class="bg-emerald-300 p-1 rounded-sm border border-slate-300 mt-2" (click)="onNotifyMeClick()">Notify me!</button>
    </div>
  `,
})
export class NotificationPreferencesComponent implements AfterViewInit {
  @ViewChild('popover') popover!: ElementRef<HTMLDivElement>;
  @ViewChild('bell') bell!: ElementRef<HTMLButtonElement>;
  protected readonly Object = Object;
  protected processUnits = this.store.selectSignal(AppSelectors.processUnits);
  protected readonly popoverWidth = 400; // When popover anchor positioning is widely available that should be used instead.
  protected readonly notificationScopes: Record<NotificationScope, NotificationScope> = {
    process_units_i_have_access_to: 'process_units_i_have_access_to',
    process_units_with_runs_ive_contributed_to: 'process_units_with_runs_ive_contributed_to',
    specific_process_units: 'specific_process_units',
  };
  protected readonly scopeControlName = 'scope';
  protected readonly topicsControlName = 'topics';
  protected readonly processUnitsControlName = 'process_units';
  protected readonly notificationTopics: Record<NotificationTopic, NotificationTopic> = {
    block_start: 'block_start',
    method_error: 'method_error',
    network_errors: 'network_errors',
    new_contributor: 'new_contributor',
    notification_cmd: 'notification_cmd',
    run_pause: 'run_pause',
    run_start: 'run_start',
    run_stop: 'run_stop',
    watch_triggered: 'watch_triggered',
  };
  protected readonly formGroup = new FormGroup({
    [this.scopeControlName]: new FormControl<NotificationScope>(this.notificationScopes.process_units_i_have_access_to),
    [this.processUnitsControlName]: new FormControl<string[]>([]),
    [this.topicsControlName]: new FormControl<NotificationTopic[]>([]),
  });
  protected bellPosition = {bottom: 0, right: 0};
  protected hasSubscription = this.swPush.subscription.pipe(map(subscription => subscription !== null));

  constructor(private store: Store,
              private webpushService: WebpushService,
              private swPush: SwPush,
              private cdRef: ChangeDetectorRef,
              private router: Router) {
    this.formGroup.valueChanges.pipe(takeUntilDestroyed()).subscribe(_ => {
      this.webpushService.saveNotificationPreferences({requestBody: this.formGroup.value as WebPushNotificationPreferences}).subscribe();
    });
    if(this.swPush.isEnabled) {
      this.swPush.notificationClicks.pipe(takeUntilDestroyed()).subscribe(click => {
        if(click.action === 'navigate') {
          void this.router.navigate([detailsUrlPart, DetailsRoutingUrlParts.processUnitUrlPart, click.notification.data.id]);
        }
      });
    }
  }

  get specificProcessUnitsSelected() {
    return this.formGroup.controls[this.scopeControlName].value === this.notificationScopes.specific_process_units;
  }

  ngAfterViewInit() {
    const bellBoundingRect = this.bell.nativeElement.getBoundingClientRect();
    this.bellPosition = {bottom: bellBoundingRect.bottom, right: bellBoundingRect.right};
  }

  onNotifyMeClick() {
    this.store.select(AppSelectors.userId).pipe(take(1)).subscribe(userId => {
      if(userId === undefined) return;
      this.webpushService.notifyUser().subscribe();
    });
  }

  async onEnabledChanged(event: Event) {
    if((event.target as HTMLInputElement).checked) {
      if(await firstValueFrom(this.hasSubscription)) return;
      this.createNewSubscription();
    } else {
      void this.swPush.unsubscribe();
    }
  }

  onBellClick() {
    this.popover.nativeElement.showPopover();
    this.webpushService.getNotificationPreferences().subscribe(preferences => {
      this.formGroup.reset(preferences, {emitEvent: false});
      this.cdRef.markForCheck();
    });
  }

  private createNewSubscription() {
    this.webpushService.getWebpushConfig().subscribe((webpushConfig) => {
      if(webpushConfig.app_server_key === undefined) {
        console.error('Could not subscribe to webpush: missing app_server_key from config from backend');
        return;
      }
      this.swPush.requestSubscription({serverPublicKey: webpushConfig.app_server_key}).then(subscription => {
        const requestBody = subscription.toJSON() as WebPushSubscription;
        this.webpushService.subscribeUser({requestBody}).subscribe();
      });
    });
  }
}
