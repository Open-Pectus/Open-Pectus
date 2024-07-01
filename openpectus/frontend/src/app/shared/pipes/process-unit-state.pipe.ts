import { Pipe, PipeTransform } from '@angular/core';
import { Error } from '../../api/models/Error';
import { InProgress } from '../../api/models/InProgress';
import { NotOnline } from '../../api/models/NotOnline';
import { Ready } from '../../api/models/Ready';
import { ProcessUnitStateEnum } from '../../typings';
import { UtilMethods } from '../util-methods';

@Pipe({
  name: 'processUnitState',
  standalone: true,
})
export class ProcessUnitStatePipe implements PipeTransform {
  transform(value: ProcessUnitStateEnum | undefined): string {
    switch(value) {
      case Ready.state.READY:
        return 'Ready';
      case InProgress.state.IN_PROGRESS:
        return 'In progress';
      case NotOnline.state.NOT_ONLINE:
        return 'Not online';
      case Error.state.ERROR:
        return 'Interrupted by error';
      case undefined:
        return '';
      default:
        return UtilMethods.assertNever(value);
    }
  }

}
