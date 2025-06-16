import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, ViewChild } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { SwPush } from '@angular/service-worker';
import { PushPipe } from '@ngrx/component';
import { concatLatestFrom } from '@ngrx/operators';
import { Store } from '@ngrx/store';
import { firstValueFrom, map, take } from 'rxjs';
import { WebpushService, WebPushSubscription } from './api';
import { AppSelectors } from './ngrx/app.selectors';

@Component({
  selector: 'app-notification-preferences',
  imports: [ReactiveFormsModule, PushPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button #bell class="codicon codicon-bell !text-xl" (click)="popover.showPopover()"></button>

    <div popover #popover class="text-black bg-white border-slate-400 text-sm p-2 border-2 rounded-lg m-0"
         [style.top.px]="bellPosition.bottom" [style.left.px]="bellPosition.right - popoverWidth" [style.width.px]="popoverWidth">
      <label>Notifications enabled for this device: <input type="checkbox" [checked]="hasSubscription | ngrxPush"
                                                           (change)="onEnabledChanged($event)"></label>
      <form class="" [formGroup]="formGroup">

      </form>
      <button class="bg-emerald-300 p-1 rounded-sm border border-slate-300" (click)="onNotifyMeClick()">Notify me!</button>
    </div>
  `,
})
export class NotificationPreferencesComponent implements AfterViewInit {
  @ViewChild('popover') popover!: ElementRef<HTMLDivElement>;
  @ViewChild('bell') bell!: ElementRef<HTMLButtonElement>;
  protected readonly popoverWidth = 300; // When popover anchor positioning is widely available that should be used instead.
  // protected readonly toggleControlName = 'toggle';
  protected readonly formGroup = new FormGroup({
    // [this.toggleControlName]: new FormControl(false),
  });
  protected bellPosition = {bottom: 0, right: 0};
  protected hasSubscription = this.swPush.subscription.pipe(map(subscription => subscription !== null));

  constructor(private store: Store,
              private webpushService: WebpushService,
              private swPush: SwPush) {}

  ngAfterViewInit() {
    const bellBoundingRect = this.bell.nativeElement.getBoundingClientRect();
    this.bellPosition = {bottom: bellBoundingRect.bottom, right: bellBoundingRect.right};
  }

  onNotifyMeClick() {
    this.store.select(AppSelectors.userId).pipe(take(1)).subscribe(userId => {
      if(userId === undefined) return;
      this.webpushService.notifyUser({userId}).subscribe();
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

  private createNewSubscription() {
    this.webpushService.getWebpushConfig().pipe(
      concatLatestFrom(() => [this.store.select(AppSelectors.userId)]),
    ).subscribe(([webpushConfig, userId]) => {
      if(webpushConfig.app_server_key === undefined) {
        console.error('Could not subscribe to webpush: missing app_server_key from config from backend');
        return;
      }
      this.swPush.requestSubscription({serverPublicKey: webpushConfig.app_server_key}).then(subscription => {
        const requestBody = subscription.toJSON() as WebPushSubscription;
        this.webpushService.subscribeUser({requestBody, userId}).subscribe();
      });
    });
  }
}
