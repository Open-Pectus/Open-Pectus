import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { MockedRequest, setupWorker } from 'msw';
import { AppModule } from './app/app.module';
import { handlers } from './msw/handlers';
import { MswEnablement } from './msw/msw-enablement';

if(MswEnablement.isEnabled) {
  const worker = setupWorker(...handlers);
  await worker.start({
    onUnhandledRequest: (request: MockedRequest) => {
      const pathname = request.url.pathname;
      if(pathname.startsWith('/assets') ||
         pathname.startsWith('/node_modules') ||
         pathname.startsWith('/src') ||
         pathname === '/codicon.ttf' ||
         pathname === '/favicon.ico' ||
         pathname.endsWith('.js') ||
         pathname.endsWith('.wasm')
      ) {
        return;
      }
      console.warn(`url ${request.url} was not mocked by MSW`);
    },
  });
}

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));
