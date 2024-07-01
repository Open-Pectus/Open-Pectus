import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'formatDurationMsec',
  standalone: true,
})
export class FormatDurationMsecPipe implements PipeTransform {
  transform(value: number | undefined): string {
    if(value === undefined) return '';
    const minutes = value / 1000 / 60;
    const seconds = (minutes % 1) * 60;
    const minutesString = Math.floor(minutes).toFixed(0);
    const secondsString = Math.floor(seconds).toFixed(0).padStart(2, '0');
    return `${minutesString}:${secondsString}`;
  }
}
