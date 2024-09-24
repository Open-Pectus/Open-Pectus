import { DecimalPipe } from '@angular/common';
import { Pipe, PipeTransform } from '@angular/core';
import { ProcessValue, ProcessValueCommandChoiceValue, ProcessValueCommandFreeTextValue, ProcessValueCommandNumberValue } from '../../api';
import { UtilMethods } from '../util-methods';

@Pipe({
  name: 'processValue',
  standalone: true,
})
export class ProcessValuePipe implements PipeTransform {
  constructor(private decimalPipe: DecimalPipe) {}

  transform(processValue: undefined |
    (Pick<ProcessValue, 'value' | 'value_type' | 'value_unit'> | ProcessValueCommandChoiceValue | ProcessValueCommandFreeTextValue | ProcessValueCommandNumberValue)
    & Pick<ProcessValue, 'value_formatted' | 'commands'>,
  ): string | null {
    if(processValue?.value === undefined) return null;

    const hasCommands = processValue.commands !== undefined && processValue.commands.length > 0;
    if(!hasCommands && processValue.value_formatted !== undefined) return processValue.value_formatted;

    const valueType = processValue.value_type;
    switch(valueType) {
      case null:
      case 'none':
        return null;
      case 'string':
      case 'choice':
        return processValue.value.toString();
      case 'float':
        return `${this.decimalPipe.transform(processValue.value, '1.2-2')} ${processValue.value_unit ?? ''}`.trim();
      case 'int':
        return `${this.decimalPipe.transform(processValue.value, '1.0-0')} ${processValue.value_unit ?? ''}`.trim();
      default:
        UtilMethods.assertNever(valueType);
    }
  }
}
