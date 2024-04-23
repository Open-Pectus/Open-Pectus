import { DatePipe, NgFor, NgIf } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, EventEmitter, Input, Output } from '@angular/core';
import { compareAsc, compareDesc } from 'date-fns';

export interface TableColumn<T> {
  key: keyof T;
  header: string;
  isDate?: boolean;
}

export enum TableSortDirection {
  Ascending = 'ascending',
  Descending = 'descending',
}

export interface DefaultTableSort<T> {
  columnKey: keyof T;
  direction: TableSortDirection;
}

@Component({
  selector: 'app-table',
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
  imports: [NgFor, NgIf],
  template: `
    <div class="bg-stone-100 rounded-md shadow-lg overflow-hidden">
      <table class="w-full table-fixed border-collapse">
        <thead>
        <tr class="bg-slate-600 text-white cursor-pointer select-none">
          <th *ngFor="let column of columns" class="px-3 py-2" (click)="setSortByColumn(column)">
            <span>{{ column.header }}</span>
            <ng-container *ngIf="sortColumn === column">
              <span *ngIf="sortDir === TableSortDirection.Descending" class="codicon codicon-arrow-up ml-1 -mr-5"></span>
              <span *ngIf="sortDir === TableSortDirection.Ascending" class="codicon codicon-arrow-down ml-1 -mr-5"></span>
            </ng-container>
          </th>
        </tr>
        </thead>
        <tbody class="cursor-pointer">
        <tr *ngFor="let row of data" class="border-y last-of-type:border-none border-gray-300" (click)="rowClicked.emit(row)">
          <td *ngFor="let column of columns" class="text-center px-3 py-2">
            {{ format(row[column.key], column) }}
          </td>
        </tr>
        </tbody>
      </table>
    </div>
  `,
})
export class TableComponent<T> {
  @Input() columns?: TableColumn<T>[];
  @Input() filter?: string;
  @Output() rowClicked = new EventEmitter<T>();
  protected sortDir = TableSortDirection.Ascending;
  protected sortColumn?: TableColumn<T>;
  protected readonly TableSortDirection = TableSortDirection;

  constructor(private datePipe: DatePipe, private cd: ChangeDetectorRef) {}

  @Input() set defaultSort(defaultSort: DefaultTableSort<T>) {
    this.sortColumn = this.columns?.find((column => column.key === defaultSort.columnKey));
    this.sortDir = defaultSort.direction;
  }

  private _data?: T[];

  get data(): T[] | undefined {
    let data = this._data;
    if(this.filter !== undefined) data = this.filterData(data, this.filter);
    if(this.sortColumn !== undefined) data = this.sortData(data, this.sortColumn);
    this.cd.markForCheck();
    return data;
  }

  @Input() set data(value: T[] | undefined) {
    this._data = structuredClone(value);
  }

  toDate(value: T[keyof T]): Date {
    if(typeof value !== 'string' && typeof value !== 'number') throw Error('Value is not Date!');
    return new Date(value);
  }

  format(value: T[keyof T], column: TableColumn<T>): string | T[keyof T] | undefined {
    if(column.isDate) return this.datePipe.transform(this.toDate(value))?.toString();
    if(Array.isArray(value)) return value.join(', ');
    return value;
  }

  setSortByColumn(column: TableColumn<T>) {
    if(this.sortColumn === column) {
      switch(this.sortDir) {
        case TableSortDirection.Ascending:
          this.sortDir = TableSortDirection.Descending;
          break;
        case TableSortDirection.Descending:
          this.sortDir = TableSortDirection.Ascending;
          break;
      }
    } else {
      this.sortColumn = column;
      this.sortDir = TableSortDirection.Ascending;
    }
  }

  private sortData(data: T[] | undefined, sortColumn: TableColumn<T>) {
    const clonedDate = structuredClone(data);
    clonedDate?.sort((a, b) => {
      const aValue = a[sortColumn.key];
      const bValue = b[sortColumn.key];
      if(sortColumn.isDate) {
        switch(this.sortDir) {
          case TableSortDirection.Ascending:
            return compareAsc(this.toDate(aValue), this.toDate(bValue));
          case TableSortDirection.Descending:
            return compareDesc(this.toDate(aValue), this.toDate(bValue));
        }
      }
      if(typeof aValue === 'string' && typeof bValue === 'string') {
        switch(this.sortDir) {
          case TableSortDirection.Ascending:
            return aValue.localeCompare(bValue);
          case TableSortDirection.Descending:
            return bValue.localeCompare(aValue);
        }
      }
      if(typeof aValue === 'number' && typeof bValue === 'number') {
        switch(this.sortDir) {
          case TableSortDirection.Ascending:
            return aValue - bValue;
          case TableSortDirection.Descending:
            return bValue - aValue;
        }
      }
      if(Array.isArray(aValue) && Array.isArray(bValue)) {
        switch(this.sortDir) {
          case TableSortDirection.Ascending:
            return aValue.toString().localeCompare(bValue.toString());
          case TableSortDirection.Descending:
            return bValue.toString().localeCompare(aValue.toString());
        }
      }
      return 0;
    });
    return clonedDate;
  }

  private filterData(data: T[] | undefined, filter: string) {
    return data?.filter(row => {
      return this.columns?.some(column => {
        const value = row[column.key];
        let stringValue = '';
        if(column.isDate) {
          stringValue = this.datePipe.transform(this.toDate(value)) ?? '';
        } else if(typeof value === 'number' || typeof value === 'string' || Array.isArray(value)) {
          stringValue = value.toString();
        }
        return stringValue.toUpperCase().includes(filter.toUpperCase());
      });
    });
  }
}
