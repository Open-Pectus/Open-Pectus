import { Pipe, PipeTransform } from '@angular/core';
import { UtilMethods } from '../util-methods';
import { ProcessUnitStateEnum } from '../../typings';
import { InProgress, NotOnline, Ready } from '../../api';

@Pipe({
  name: 'processUnitState',
})
export class ProcessUnitStatePipe implements PipeTransform {

  transform(value: ProcessUnitStateEnum | undefined, ...args: unknown[]): string {
    if(value === undefined) return '';
    switch(value) {
      case Ready.state.READY:
        return 'Ready';
      case InProgress.state.IN_PROGRESS:
        return 'In Progress';
      case NotOnline.state.NOT_ONLINE:
        return 'Not Online';
      default:
        return UtilMethods.assertNever(value);
    }
  }

}
