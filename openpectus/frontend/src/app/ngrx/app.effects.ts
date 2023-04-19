import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { AppActions } from './app.actions';
import { map } from 'rxjs';

@Injectable()
export class AppEffects {
  testEffect = createEffect(() => this.actions.pipe(
    ofType(AppActions.aTestAction),
    map(({aString}) => {
      window.alert(aString);
    })
  ), {dispatch: false});

  constructor(private actions: Actions) {}
}
