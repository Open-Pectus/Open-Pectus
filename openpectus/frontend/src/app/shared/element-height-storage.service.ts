import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class ElementHeightStorageService {
  saveHeight(name: string | undefined, height: number) {
    if(name === undefined) return;
    localStorage.setItem(this.transformName(name), height.toString());
  }

  getHeight(name: string) {
    const item = localStorage.getItem(this.transformName(name));
    if(item === null) return item;
    return parseInt(item);
  }

  private transformName(name: string) {
    return `[${window.location.pathname}] ${name} element height`;
  }
}
