import { ChangeDetectionStrategy, ChangeDetectorRef, Component, computed, ElementRef, ViewChild } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SwPush } from '@angular/service-worker';
import { PushPipe } from '@ngrx/component';
import { Store } from '@ngrx/store';
import { firstValueFrom, map } from 'rxjs';
import { NotificationScope, NotificationTopic, WebPushNotificationPreferences, WebpushService, WebPushSubscription } from './api';
import { detailsUrlPart } from './app.routes';
import { DetailsRoutingUrlParts } from './details/details-routing-url-parts';
import { AppSelectors } from './ngrx/app.selectors';
import { notificationScopes, topics } from './notification.types';
import { MultiSelectComponent } from './shared/multi-select.component';
import { UtilMethods } from './shared/util-methods';

@Component({
  selector: 'app-notification-preferences',
  imports: [ReactiveFormsModule, PushPipe, MultiSelectComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button #bell class="codicon codicon-bell !text-xl" (click)="onBellClick()"></button>

    <div popover #popover
         class="text-black bg-white border-slate-400 p-3.5 border rounded-lg m-0 shadow-lg shadow-slate-500 outline outline-4 outline-slate-300"
         [style.top.px]="bellPosition.bottom" [style.left.px]="popoverLeft" [style.width.px]="popoverWidth">
      <label class="flex items-center gap-2">
        <input type="checkbox" [checked]="hasSubscription | ngrxPush" class="w-5 h-5 accent-blue-500"
               (change)="onEnabledChanged($event)"> Notifications enabled (this device)
      </label>
      <form [formGroup]="formGroup">
        <div class="flex flex-col gap-0.5">
          <h1 class="font-bold mt-4">Scopes:</h1>
          <label class="flex items-center gap-2">
            <input type="radio" [value]="notificationScopes.process_units_i_have_access_to" class="w-5 h-5 accent-blue-500"
                   [formControlName]="scopeControlName"> Process Units I have access to
          </label>
          <label class="flex items-center gap-2">
            <input type="radio" [value]="notificationScopes.process_units_with_runs_ive_contributed_to" class="w-5 h-5 accent-blue-500"
                   [formControlName]="scopeControlName"> Process Units I have contributed to
          </label>
          <label class="flex items-center gap-2">
            <input type="radio" [value]="notificationScopes.specific_process_units" class="w-5 h-5 accent-blue-500"
                   [formControlName]="scopeControlName"> Specific Process Units:
          </label>
          @if (specificProcessUnitsSelected) {
            <app-multi-select class="ml-7 border-l pl-3.5 border-slate-400" [formControlName]="processUnitsControlName"
                              [options]="processUnitOptions()"></app-multi-select>
          }
        </div>

        <div class="flex flex-col">
          <h1 class="font-bold mt-4 mb-0.5">Topics:</h1>
          <app-multi-select [formControlName]="topicsControlName" [options]="topicOptions"></app-multi-select>
        </div>
      </form>
      <button class="bg-green-300 py-1.5 px-2.5 rounded-md border-slate-400 absolute right-4 bottom-4" (click)="onNotifyMeClick()">
        Notify me!
      </button>
    </div>
  `,
})
export class NotificationPreferencesComponent {
  @ViewChild('popover') popover!: ElementRef<HTMLDivElement>;
  @ViewChild('bell') bell!: ElementRef<HTMLButtonElement>;
  protected readonly notificationScopes = notificationScopes;
  protected readonly popoverWidth = 350; // When popover anchor positioning is widely available that should be used instead.

  protected bellPosition = {bottom: 0, right: 0};
  protected processUnits = this.store.selectSignal(AppSelectors.processUnits);
  protected processUnitOptions = computed(() => this.processUnits().map(processUnit => ({name: processUnit.name, value: processUnit.id})));
  protected readonly scopeControlName = 'scope';
  protected readonly topicsControlName = 'topics';
  protected readonly processUnitsControlName = 'process_units';
  protected readonly topicOptions = Object.values(topics).map(topic => {
    return {value: topic, name: UtilMethods.titleCase(topic.replace('_', ' '))};
  });
  protected readonly formGroup = new FormGroup({
    [this.scopeControlName]: new FormControl<NotificationScope>(notificationScopes.process_units_i_have_access_to),
    [this.processUnitsControlName]: new FormControl<string[]>([]),
    [this.topicsControlName]: new FormControl<NotificationTopic[]>([]),
  });
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
          void this.router.navigate([detailsUrlPart, DetailsRoutingUrlParts.processUnitUrlPart, click.notification.data.process_unit_id]);
        }
      });
    }
  }

  get popoverLeft() {
    return Math.max(this.bellPosition.right - this.popoverWidth, 4); // 4 because of outline width of 4
  }

  get specificProcessUnitsSelected() {
    return this.formGroup.controls[this.scopeControlName].value === notificationScopes.specific_process_units;
  }

  async onNotifyMeClick() {
    const userId = await firstValueFrom(this.store.select(AppSelectors.userId));
    const processUnitId = await firstValueFrom(this.store.select(AppSelectors.processUnits).pipe(map(processUnits => processUnits[0].id)));
    if(userId === undefined) return;
    this.webpushService.notifyUser({processUnitId: processUnitId}).subscribe();
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
    const bellBoundingRect = this.bell.nativeElement.getBoundingClientRect();
    this.bellPosition = {bottom: bellBoundingRect.bottom, right: bellBoundingRect.right};
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
