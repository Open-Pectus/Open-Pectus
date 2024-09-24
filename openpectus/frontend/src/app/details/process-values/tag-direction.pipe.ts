import { Pipe, PipeTransform } from '@angular/core';
import { TagDirection } from '../../api';
import { UtilMethods } from '../../shared/util-methods';

@Pipe({
  name: 'tagDirection',
  standalone: true,
})
export class TagDirectionPipe implements PipeTransform {

  transform(value: TagDirection): string {
    switch(value) {
      case 'input':
        return 'Input';
      case 'output':
        return 'Output';
      case 'na':
        return 'N/A';
      case 'unspecified':
        return 'Unspecified';
      default:
        return UtilMethods.assertNever(value);
    }
  }

}
