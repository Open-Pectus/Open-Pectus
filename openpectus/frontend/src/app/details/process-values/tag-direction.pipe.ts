import { Pipe, PipeTransform } from '@angular/core';
import { TagDirection } from '../../api/models/TagDirection';

@Pipe({
  name: 'tagDirection',
  standalone: true,
})
export class TagDirectionPipe implements PipeTransform {

  transform(value: string): string {
    switch(value) {
      case TagDirection.INPUT:
        return 'Input';
      case TagDirection.OUTPUT:
        return 'Output';
      case TagDirection.NA:
        return 'N/A';
      case TagDirection.UNSPECIFIED:
        return 'Unspecified';
      default:
        return '';
    }
  }

}
