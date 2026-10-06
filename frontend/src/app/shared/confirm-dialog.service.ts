import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ConfirmDialogService {
  ask(message: string, buttons: string[]): Promise<string> {
    const dlg = document.createElement('dialog');
    dlg.className = 'rounded-md border-2 border-gray-400 p-4 shadow-md shadow-gray-400 text-center mt-[10vh] mb-auto';
    dlg.innerHTML = `<p class="mb-3 whitespace-pre-line"></p><div class="flex gap-2 justify-center"></div>`;
    dlg.querySelector('p')!.textContent = message;
    const row = dlg.querySelector('div')!;
    return new Promise(resolve => {
      buttons.forEach(b => {
        const btn = document.createElement('button');
        btn.textContent = b;
        btn.className = 'rounded p-1 px-3 bg-sky-700 text-white';
        btn.onclick = () => { dlg.close(); resolve(b); };
        row.appendChild(btn);
      });
      dlg.addEventListener('close', () => { dlg.remove(); resolve('dismissed'); }, { once: true });
      document.body.appendChild(dlg);
      dlg.showModal();
    });
  }
}