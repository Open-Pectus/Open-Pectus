import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Store } from '@ngrx/store';
import { AppActions } from './ngrx/app.actions';
import { TopBarComponent } from './top-bar.component';

@Component({
  selector: 'app-root',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [TopBarComponent, RouterOutlet],
  template: `
    <app-top-bar />
    <router-outlet />
  `,
})
export class AppComponent implements OnInit {
  private store = inject(Store);


  ngOnInit() {
    this.store.dispatch(AppActions.pageInitialized());
  }
}
