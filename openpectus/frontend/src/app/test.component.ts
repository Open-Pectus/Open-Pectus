import { ChangeDetectionStrategy, Component } from '@angular/core';
import { AppSelectors } from './ngrx/app.selectors';
import { selectQueryParam } from './ngrx/router.selectors';
import { Store } from '@ngrx/store';
import { AppActions } from './ngrx/app.actions';
import { tap } from 'rxjs';

@Component({
  selector: 'app-test',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="bg-red-600" (click)="onClick()">
      {{aString | ngrxPush}}
      {{route | ngrxPush}}
    </div>
  `
})
export class TestComponent {
  aString = this.store.select(AppSelectors.aString);
  route = this.store.select(selectQueryParam('q')).pipe(tap(url => console.log(url)));

  constructor(private store: Store) {}

  onClick() {
    this.store.dispatch(AppActions.aTestAction({aString: 'a new string'}));
  }

}
