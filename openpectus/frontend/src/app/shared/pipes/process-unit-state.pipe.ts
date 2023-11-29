import { Pipe, PipeTransform } from '@angular/core';
import { InProgress, NotOnline, Ready } from '../../api';
import { ProcessUnitStateEnum } from '../../typings';
import { UtilMethods } from '../util-methods';

@Pipe({
  name: 'processUnitState',
  standalone: true,
})
export class ProcessUnitStatePipe implements PipeTransform {
  transform(value: ProcessUnitStateEnum | undefined, ...args: unknown[]): string {
    switch(value) {
      case Ready.state.READY:
        return 'Ready';
      case InProgress.state.IN_PROGRESS:
        return 'In Progress';
      case NotOnline.state.NOT_ONLINE:
        return 'Not Online';
      case undefined:
        return '';
      default:
        return UtilMethods.assertNever(value);
    }
  }

}
