import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { AppSelectors } from './ngrx/app.selectors';
import { AppActions } from './ngrx/app.actions';

@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'app-root',
  template: `
    <div class="bg-red-600" (click)="onClick()">
      {{aString | ngrxPush}}
    </div>
  `
})
export class AppComponent {
  aString = this.store.select(AppSelectors.aString);

  constructor(private store: Store) {}

  onClick() {
    this.store.dispatch(AppActions.aTestAction({aString: 'a new string'}));
  }
}
