import { ChangeDetectionStrategy, Component } from '@angular/core';
import { AppSelectors } from './ngrx/app.selectors';
import { selectQueryParam } from './ngrx/router.selectors';
import { Store } from '@ngrx/store';
import { AppActions } from './ngrx/app.actions';

@Component({
  selector: 'app-test',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="bg-blue-300" (click)="onClick()">
      {{aString | ngrxPush}}
      {{queryParam | ngrxPush}}
    </div>
  `
})
export class TestComponent {
  aString = this.store.select(AppSelectors.aString);
  queryParam = this.store.select(selectQueryParam('q'));

  constructor(private store: Store) {}

  onClick() {
    this.store.dispatch(AppActions.aTestAction({aString: 'a new string'}));
  }

}
